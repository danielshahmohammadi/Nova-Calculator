"""Scientific functions with configurable degree/radian angle mode."""
import math


class ScientificFunctions:
    def __init__(self, angle_mode: str = "DEG"):
        self.set_angle_mode(angle_mode)

    def set_angle_mode(self, mode: str) -> None:
        normalized = str(mode).strip().upper()
        if normalized not in {"DEG", "RAD"}:
            raise ValueError("حالت زاویه باید DEG یا RAD باشد.")
        self.angle_mode = normalized

    def _to_radians(self, value: float) -> float:
        return math.radians(value) if self.angle_mode == "DEG" else value

    def sin(self, value: float) -> float:
        return math.sin(self._to_radians(value))

    def cos(self, value: float) -> float:
        return math.cos(self._to_radians(value))

    def tan(self, value: float) -> float:
        angle = self._to_radians(value)
        if math.isclose(math.cos(angle), 0.0, abs_tol=1e-12):
            raise ValueError("تانژانت در این زاویه تعریف نشده است.")
        return math.tan(angle)

    def _from_radians(self, value: float) -> float:
        return math.degrees(value) if self.angle_mode == "DEG" else value

    def asin(self, value: float) -> float:
        return self._from_radians(math.asin(value))

    def acos(self, value: float) -> float:
        return self._from_radians(math.acos(value))

    def atan(self, value: float) -> float:
        return self._from_radians(math.atan(value))

    @staticmethod
    def sqrt(value: float) -> float:
        if value < 0:
            raise ValueError("ریشه دوم عدد منفی در اعداد حقیقی تعریف نشده است.")
        return math.sqrt(value)

    @staticmethod
    def log(value: float, base: float = 10) -> float:
        if value <= 0 or base <= 0 or base == 1:
            raise ValueError("ورودی لگاریتم یا پایه آن نامعتبر است.")
        return math.log(value, base)

    @staticmethod
    def ln(value: float) -> float:
        if value <= 0:
            raise ValueError("لگاریتم طبیعی فقط برای اعداد مثبت تعریف شده است.")
        return math.log(value)

    @staticmethod
    def factorial(value: float) -> int:
        if value < 0 or not float(value).is_integer():
            raise ValueError("فاکتوریل فقط برای اعداد صحیح نامنفی تعریف شده است.")
        if value > 170:
            raise OverflowError("عدد برای محاسبه فاکتوریل بیش از حد بزرگ است.")
        return math.factorial(int(value))

    @staticmethod
    def abs(value: float) -> float:
        return abs(value)

    @staticmethod
    def exp(value: float) -> float:
        return math.exp(value)
