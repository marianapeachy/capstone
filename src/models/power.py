"""Evita que Windows trate el entrenamiento como proceso de fondo.

Windows 11 aplica EcoQoS a los procesos sin ventana en primer plano (por
ejemplo, uno lanzado desacoplado para que sobreviva a la sesion) y, en
CPUs hibridas como la i5-13400F, los manda a los nucleos de eficiencia.
Con batch 1 el entrenamiento depende de un solo hilo (el proceso
principal lanza los kernels), asi que eso bajaba P2 de ~7 a ~3,7 it/s con
la GPU a la mitad. Medido el 2026-10-01.
"""

from __future__ import annotations

import ctypes
import sys

_PROCESS_POWER_THROTTLING = 4  # PROCESS_INFORMATION_CLASS.ProcessPowerThrottling
_EXECUTION_SPEED = 0x1  # PROCESS_POWER_THROTTLING_EXECUTION_SPEED


class _PowerThrottlingState(ctypes.Structure):
    _fields_ = [("Version", ctypes.c_ulong), ("ControlMask", ctypes.c_ulong), ("StateMask", ctypes.c_ulong)]


def disable_eco_qos() -> bool:
    """Desactiva EcoQoS en el proceso actual. Devuelve False fuera de Windows o si falla."""
    if sys.platform != "win32":
        return False
    kernel32 = ctypes.windll.kernel32
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    # ControlMask dice que politica se controla; StateMask=0 la desactiva.
    state = _PowerThrottlingState(1, _EXECUTION_SPEED, 0)
    return bool(
        kernel32.SetProcessInformation(
            ctypes.c_void_p(kernel32.GetCurrentProcess()),
            _PROCESS_POWER_THROTTLING,
            ctypes.byref(state),
            ctypes.sizeof(state),
        )
    )
