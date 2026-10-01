import sys

from src.models.power import disable_eco_qos


def test_disable_eco_qos_applies_only_on_windows():
    # Afecta solo al proceso de pytest; en Windows debe aceptarlo el kernel.
    assert disable_eco_qos() is (sys.platform == "win32")
