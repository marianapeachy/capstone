import pytest
import torch

from src.models.vram import cpu_fallback_on_oom, vram_fraction

GIB = 2**30


def test_vram_fraction_leaves_the_reserve_free():
    assert vram_fraction(8 * GIB, reserve_gib=1.5) == pytest.approx(6.5 / 8)


def test_vram_fraction_never_goes_below_the_minimum():
    assert vram_fraction(2 * GIB, reserve_gib=1.5, minimum=0.5) == 0.5


def _recording_forward(fail_first_with=None):
    calls = []

    def forward(self, *tensors):
        calls.append([t.device.type for t in tensors])
        if fail_first_with is not None and len(calls) == 1:
            raise fail_first_with
        return tuple(t * 2 for t in tensors)

    return forward, calls


def test_without_oom_the_original_forward_runs_once():
    forward, calls = _recording_forward()
    wrapped = cpu_fallback_on_oom(forward)
    out = wrapped(None, torch.ones(2), torch.ones(3))
    assert len(calls) == 1
    assert torch.equal(out[0], torch.full((2,), 2.0))


def test_on_oom_it_retries_on_cpu_and_returns_to_the_input_device():
    forward, calls = _recording_forward(torch.OutOfMemoryError("CUDA out of memory"))
    wrapped = cpu_fallback_on_oom(forward)
    a, b = torch.ones(2), torch.ones(3)
    out = wrapped(None, a, b)
    assert len(calls) == 2
    assert calls[1] == ["cpu", "cpu"]
    assert all(o.device == a.device for o in out)
    assert torch.equal(out[1], torch.full((3,), 2.0))


def test_other_runtime_errors_are_not_swallowed():
    forward, calls = _recording_forward(RuntimeError("shape mismatch"))
    with pytest.raises(RuntimeError, match="shape mismatch"):
        cpu_fallback_on_oom(forward)(None, torch.ones(1))
    assert len(calls) == 1
