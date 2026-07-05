"""Unit tests for DVC data version parsing utility."""
import tempfile
from pathlib import Path


def parse_dvc_md5(dvc_file_path: Path) -> str:
    """Parse the md5 hash from a .dvc pointer file. Mirrors train.py logic."""
    for line in dvc_file_path.read_text().splitlines():
        if "md5:" in line:
            return line.split("md5:")[1].strip()
    return "unknown"


class TestDvcVersionParsing:
    """Test that DVC pointer file md5 extraction works correctly."""

    def test_extracts_md5_from_valid_dvc_file(self):
        """A valid .dvc file with an md5 field should return the hash."""
        content = """outs:
- md5: abc123def456
  size: 12345
  path: data.csv"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dvc", delete=False
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            result = parse_dvc_md5(tmp_path)
            assert result == "abc123def456"
        finally:
            tmp_path.unlink()

    def test_returns_unknown_when_no_md5(self):
        """A .dvc file without md5 should return 'unknown'."""
        content = """outs:
- size: 12345
  path: data.csv"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dvc", delete=False
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            result = parse_dvc_md5(tmp_path)
            assert result == "unknown"
        finally:
            tmp_path.unlink()

    def test_returns_unknown_for_empty_file(self):
        """An empty .dvc file should return 'unknown'."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dvc", delete=False
        ) as f:
            f.write("")
            tmp_path = Path(f.name)

        try:
            result = parse_dvc_md5(tmp_path)
            assert result == "unknown"
        finally:
            tmp_path.unlink()
