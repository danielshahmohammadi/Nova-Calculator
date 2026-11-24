"""Persistent JSON calculation history."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CalculationHistory:
    def __init__(self, file_path: str | Path | None = None, max_items: int = 500):
        if max_items < 1:
            raise ValueError("max_items باید حداقل ۱ باشد.")
        self.file_path = Path(file_path) if file_path else (
            Path.home() / "AppData" / "Local" / "NOVA Calculator" / "history.json"
        )
        self.max_items = max_items
        self._items: list[dict[str, Any]] = []
        self.load()

    def load(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            self._items = []
            return self.get_all()
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                raise ValueError("ساختار فایل تاریخچه معتبر نیست.")
            valid = []
            for item in data:
                if (isinstance(item, dict)
                        and isinstance(item.get("expression"), str)
                        and isinstance(item.get("result"), (int, float))
                        and not isinstance(item.get("result"), bool)):
                    valid.append(item)
            self._items = valid[-self.max_items:]
        except (json.JSONDecodeError, OSError, ValueError):
            # Keep the application usable if the history file is damaged.
            self._items = []
        return self.get_all()

    def add(self, expression: str, result: float) -> dict[str, Any]:
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("عبارت محاسبه نمی‌تواند خالی باشد.")
        numeric_result = float(result)
        if numeric_result != numeric_result or numeric_result in (float("inf"), float("-inf")):
            raise ValueError("نتیجه باید یک عدد متناهی باشد.")
        item = {
            "expression": expression.strip(),
            "result": numeric_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._items.append(item)
        self._items = self._items[-self.max_items:]
        self.save()
        return dict(item)

    def get_all(self) -> list[dict[str, Any]]:
        return [dict(item) for item in reversed(self._items)]

    def clear(self) -> None:
        self._items.clear()
        self.save()

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self._items, ensure_ascii=False, indent=2)
        fd, temp_name = tempfile.mkstemp(
            prefix=self.file_path.name, suffix=".tmp", dir=str(self.file_path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_name, self.file_path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
