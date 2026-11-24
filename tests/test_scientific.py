import pytest
from backend.scientific import ScientificFunctions


def test_degree_trigonometry():
    sci = ScientificFunctions("DEG")
    assert sci.sin(90) == pytest.approx(1)
    assert sci.cos(180) == pytest.approx(-1)


def test_invalid_angle_mode():
    sci = ScientificFunctions()
    with pytest.raises(ValueError):
        sci.set_angle_mode("GRAD")


def test_factorial_validation():
    sci = ScientificFunctions()
    with pytest.raises(ValueError):
        sci.factorial(-1)
    with pytest.raises(ValueError):
        sci.factorial(2.5)


def test_inverse_trig_angle_mode():
    sci = ScientificFunctions("RAD")
    assert sci.asin(1) == pytest.approx(1.5707963267948966)
