"""Stream a very large image to a BigTIFF, a strip at a time.

Ultra Detail produces images past 4 GB (a 600 MP 16-bit RGB is ~3.7 GB) that
cannot be held in RAM to hand to an encoder in one call — that is the freeze the
in-memory save caused. BigTIFF lifts TIFF's 4 GB limit, and ``tifffile.memmap`` lets us write the file
in place through a numpy memmap: fill it a block at a time, so only one block is
ever resident and the OS pages the rest to disk. It is written **uncompressed**,
which is a feature here — the giant PNG's zlib pass was the slow, CPU-bound step
that froze the save; a memmapped uncompressed write is near-zero CPU and bounded
RAM. The file is large (a 600 MP 16-bit image is ~3.7 GB) but that is the honest
cost of a lossless image that size.

The rows arrive already finished (merged, graded, display-referred sRGB in
``[0, 1]``); this only quantises each block to the chosen bit depth and writes
it, so nothing image-specific lives here.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import numpy as np


def write_streaming(
    path: Path,
    height: int,
    width: int,
    rows: Iterator[tuple[int, np.ndarray]],
    *,
    bits: int = 16,
) -> None:
    """Write ``height×width`` RGB to a BigTIFF from an iterator of row blocks.

    ``rows`` yields ``(y0, block)`` where ``block`` is a ``(n, width, 3)`` float
    array in sRGB ``[0, 1]`` and ``y0`` its top row, together covering every row
    exactly once. ``bits`` is 16 (default) or 8.
    """
    import tifffile

    dtype = np.uint16 if bits == 16 else np.uint8
    scale = 65535.0 if bits == 16 else 255.0

    path.parent.mkdir(parents=True, exist_ok=True)
    # Creates the file and returns a memmap into its pixel data. Uncompressed and
    # bigtiff so it can exceed 4 GB and be written by slicing.
    array = tifffile.memmap(
        str(path), shape=(height, width, 3), dtype=dtype,
        photometric="rgb", bigtiff=True,
    )
    try:
        for y0, block in rows:
            n = block.shape[0]
            array[y0:y0 + n] = np.round(np.clip(block, 0.0, 1.0) * scale).astype(dtype)
        array.flush()
    finally:
        # Drop the memmap so the file handle/lock is released (Windows).
        del array
