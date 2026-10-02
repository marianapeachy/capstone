"""Limite de memoria de video para entrenar en GPUs chicas bajo Windows.

En Windows (WDDM), cuando una asignacion CUDA no cabe en la GPU el driver
no lanza "out of memory": pagina a la RAM compartida. La GPU marca 100% de
uso pero baja a ~40 W y el entrenamiento va ~18 veces mas lento. Ademas,
Ultralytics solo vacia la cache de PyTorch al final de cada epoca, asi que
un pico deja el resto de la epoca paginando.

En SKU-110K el pico lo produce el asignador de la perdida
(TaskAlignedAssigner) en las imagenes con cientos de productos: arma
tensores de (cajas anotadas x anclas), y la variante P2 tiene ~136 mil
anclas a 1280 px. Con batch 1, Ultralytics ya no puede partir el batch.

Solucion: limitar la memoria de PyTorch por debajo de la fisica, para que
el pico lance un OOM real en vez de paginar, y resolver ese caso en CPU.
"""

from __future__ import annotations

import functools

import torch

GIB = 2**30


def vram_fraction(total_bytes: int, reserve_gib: float = 1.5, minimum: float = 0.5) -> float:
    """Fraccion de la GPU para PyTorch dejando `reserve_gib` libres (SO, pantalla, contexto CUDA)."""
    return max(minimum, (total_bytes - reserve_gib * GIB) / total_bytes)


def _is_oom(error: RuntimeError) -> bool:
    return isinstance(error, torch.OutOfMemoryError) or "out of memory" in str(error).lower()


def cpu_fallback_on_oom(forward):
    """Envuelve un forward de tensores: si se queda sin memoria, lo repite en CPU."""

    @functools.wraps(forward)
    def wrapper(self, *tensors):
        try:
            return forward(self, *tensors)
        except RuntimeError as e:
            if not _is_oom(e):
                raise
        # Fuera del except: asi el traceback suelta los intermedios del intento fallido.
        device = tensors[0].device
        if device.type == "cuda":
            torch.cuda.empty_cache()
        result = forward(self, *(t.cpu() for t in tensors))
        return tuple(t.to(device) for t in result)

    wrapper.cpu_fallback = True
    return wrapper


def limit_vram(device: str, reserve_gib: float = 1.5) -> str | None:
    """Limita la memoria de PyTorch en `device` y activa el asignador en CPU ante OOM.

    Devuelve un resumen para el log, o None si no aplica (CPU o varias GPUs).
    """
    if device == "cpu" or "," in device or not torch.cuda.is_available():
        return None
    from ultralytics.utils.tal import TaskAlignedAssigner

    index = int(device) if device.isdigit() else 0
    total = torch.cuda.get_device_properties(index).total_memory
    fraction = vram_fraction(total, reserve_gib)
    torch.cuda.set_per_process_memory_fraction(fraction, index)
    if not getattr(TaskAlignedAssigner.forward, "cpu_fallback", False):
        TaskAlignedAssigner.forward = cpu_fallback_on_oom(TaskAlignedAssigner.forward)
    return f"VRAM de PyTorch limitada a {fraction * total / GIB:.2f} de {total / GIB:.2f} GiB; asignador a CPU ante OOM"
