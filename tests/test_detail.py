"""Detail utilities: the frequency-graft blend and the unsharp fallback.

``preserve_detail`` and ``sharpen`` are retained image-space helpers — sharpen
is the crispen step Boost/Ultra run before the neural pass. The Preserve *mode*
was retired; these tests cover the maths, plus the settings migration off it.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from dlss5_converter import detail
from dlss5_converter.settings import AppSettings, DetailSettings


def _sharp_lines(size=128):
    yy, xx = np.mgrid[0:size, 0:size]
    pat = ((xx // 3) % 2).astype(np.float32)  # crisp 3px vertical bars
    return np.repeat(pat[:, :, None], 3, axis=2)


def _sharpness(img):
    g = cv2.cvtColor((np.clip(img, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(g.astype(np.float32), cv2.CV_32F).var()


def test_preserve_amount_zero_is_a_passthrough():
    result = _sharp_lines()
    assert detail.preserve_detail(result, result, amount=0.0) is result


def test_preserve_restores_softened_detail():
    source = _sharp_lines()
    softened = cv2.GaussianBlur(source, (0, 0), 1.5)  # stand in for DLAA softening
    restored = detail.preserve_detail(softened, source, amount=1.0)
    # The restored image is much sharper than the softened one, and close to the
    # source it lifted the detail from.
    assert _sharpness(restored) > _sharpness(softened) * 1.5
    assert _sharpness(restored) == pytest.approx(_sharpness(source), rel=0.15)


def test_preserve_stays_in_range_and_never_overshoots_beyond_source():
    source = _sharp_lines()
    softened = cv2.GaussianBlur(source, (0, 0), 1.5)
    restored = detail.preserve_detail(softened, source, amount=1.0)
    assert restored.min() >= 0.0 and restored.max() <= 1.0


def test_preserve_requires_matching_sizes():
    a = _sharp_lines(128)
    b = _sharp_lines(64)
    with pytest.raises(ValueError, match="matching sizes"):
        detail.preserve_detail(a, b, amount=1.0)


def test_preserve_range_keeps_hdr_highlights():
    source = _sharp_lines() * 3.0  # scene-referred, above 1.0
    softened = cv2.GaussianBlur(source, (0, 0), 1.5)
    restored = detail.preserve_detail(softened, source, amount=1.0, preserve_range=True)
    assert restored.max() > 1.5  # not crushed to white


def test_sharpen_amount_zero_is_a_passthrough():
    img = _sharp_lines()
    assert detail.sharpen(img, amount=0.0) is img


def test_sharpen_increases_acutance():
    img = cv2.GaussianBlur(_sharp_lines(), (0, 0), 1.2)
    assert _sharpness(detail.sharpen(img, amount=1.5)) > _sharpness(img)


def test_detail_settings_round_trip(tmp_path):
    path = tmp_path / "settings.json"
    a = AppSettings()
    a.detail.mode = "ultra"
    a.detail.ultra_max_factor = 3.0
    a.save(path)
    b = AppSettings.load(path)
    assert b.detail.mode == "ultra"
    assert b.detail.ultra_max_factor == pytest.approx(3.0)
    assert AppSettings().detail.is_neutral  # default is off


def test_old_preserve_mode_migrates_to_off():
    """Settings from a build that had Preserve must not leave the pipeline in an
    unknown mode — __post_init__ maps the retired value to off."""
    assert DetailSettings(mode="preserve").mode == "off"
    assert DetailSettings(mode="nonsense").mode == "off"
    assert DetailSettings(mode="boost").mode == "boost"


def test_old_settings_file_with_retired_keys_still_loads(tmp_path):
    """A v0.3.x settings.json carrying amount/supersample/preserve loads clean:
    unknown keys are dropped and the mode is migrated."""
    path = tmp_path / "settings.json"
    path.write_text(
        '{"detail": {"mode": "preserve", "amount": 0.9, "supersample": 8}}',
        encoding="utf-8",
    )
    loaded = AppSettings.load(path)
    assert loaded.detail.mode == "off"
    assert loaded.detail.is_neutral
