"""Smoke tests to verify the package is importable and correctly configured."""

from swaplm import __version__


def test_version_is_string():
    """Version should be a non-empty string."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Version should follow semver (major.minor.patch)."""
    parts = __version__.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()


def test_py_typed_exists():
    """Package should include PEP 561 py.typed marker file."""
    import pathlib

    import swaplm

    pkg_dir = pathlib.Path(swaplm.__file__).parent
    assert (pkg_dir / "py.typed").exists()
