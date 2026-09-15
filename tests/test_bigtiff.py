"""Streaming BigTIFF writer: what goes in as row blocks comes back as pixels."""

from __future__ import annotations

import numpy as np
import pytest

from dlss5_converter import bigtiff

tifffile = pytest.importorskip("tifffile")


def _blocks(img, block):
    for y0 in range(0, img.shape[0], block):
        yield y0, img[y0:y0 + block]


def test_streaming_write_roundtrips_16bit(tmp_path):
    h, w = 500, 300
    rng = np.random.default_rng(0)
    img = rng.random((h, w, 3), dtype=np.float32)
    out = tmp_path / "big.tiff"
    # Odd block size, to prove arbitrary blocks land at the right rows.
    bigtiff.write_streaming(out, h, w, _blocks(img, 111), bits=16)

    back = tifffile.imread(str(out))
    assert back.shape == (h, w, 3)
    assert back.dtype == np.uint16
    expected = np.round(np.clip(img, 0, 1) * 65535).astype(np.uint16)
    assert np.array_equal(back, expected)


def test_streaming_write_is_bigtiff(tmp_path):
    out = tmp_path / "big.tiff"
    img = np.zeros((64, 64, 3), np.float32)
    bigtiff.write_streaming(out, 64, 64, _blocks(img, 64))
    with tifffile.TiffFile(str(out)) as tif:
        assert tif.is_bigtiff


def test_streaming_write_8bit(tmp_path):
    h, w = 200, 200
    img = np.full((h, w, 3), 0.5, np.float32)
    out = tmp_path / "small.tiff"
    bigtiff.write_streaming(out, h, w, _blocks(img, 60), bits=8)
    back = tifffile.imread(str(out))
    assert back.dtype == np.uint8
    assert abs(int(back[0, 0, 0]) - 128) <= 1
