"""Three-way Style, the style-tagged filename, and the Boost size guard."""

from __future__ import annotations

from pathlib import Path

from dlss5_converter import pipeline
from dlss5_converter.settings import (
    NR_STYLES,
    style_slug,
)


def test_style_list_is_the_addons_three():
    """Default, Natural, Cinematic - Default is index 0, the add-on's own start."""
    assert NR_STYLES == ("Default", "Natural", "Cinematic")


def test_style_slug_names_each_style_and_clamps():
    assert style_slug(0) == "default"
    assert style_slug(1) == "natural"
    assert style_slug(2) == "cinematic"
    # A stored index past the end still yields a name rather than raising.
    assert style_slug(99) == "cinematic"
    assert style_slug(-3) == "default"


def test_output_name_carries_the_style(tmp_path):
    out = pipeline.hdr_output_path(tmp_path, "shot", tmp_path / "shot.png", "cinematic")
    assert out.name == "shot_dlss5_cinematic.png"
    # HDR input keeps the format that can hold it, still tagged.
    hdr = pipeline.hdr_output_path(tmp_path, "shot", tmp_path / "shot.jxr", "natural")
    assert hdr.name == "shot_dlss5_natural.jxr"


def test_output_name_without_a_style_is_unchanged(tmp_path):
    """The default-None call still produces the old name, so nothing else breaks."""
    out = pipeline.hdr_output_path(tmp_path, "shot", tmp_path / "shot.png")
    assert out.name == "shot_dlss5.png"


def test_output_format_override_forces_the_extension(tmp_path):
    """Apply-to-folder's 'Save as' choice overrides the source-derived type."""
    # SDR source, forced to JPEG.
    out = pipeline.hdr_output_path(tmp_path, "shot", tmp_path / "shot.png", "cinematic", fmt="jpg")
    assert out.name == "shot_dlss5_cinematic.jpg"
    # HDR source that would default to .jxr, forced to PNG.
    out = pipeline.hdr_output_path(tmp_path, "shot", tmp_path / "shot.jxr", fmt="png")
    assert out.name == "shot_dlss5.png"
    # A leading dot in the format is tolerated.
    out = pipeline.hdr_output_path(tmp_path, "shot", tmp_path / "shot.png", fmt=".tif")
    assert out.name == "shot_dlss5.tif"
