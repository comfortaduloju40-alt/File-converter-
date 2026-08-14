"""
Wraps `soffice --headless --convert-to` for document conversions.

Supported source -> target formats are declared in EXTENSION_TARGETS below.
Add more pairs there as needed; the conversion call itself is generic.
"""

import subprocess
import uuid
from pathlib import Path

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

EXTENSION_TARGETS: dict[str, list[str]] = {
    "pdf": ["docx", "xlsx", "pptx"],
    "docx": ["pdf"],
    "doc": ["pdf", "docx"],
    "xlsx": ["pdf"],
    "xls": ["pdf", "xlsx"],
    "pptx": ["pdf"],
    "ppt": ["pdf", "pptx"],
    "odt": ["pdf", "docx"],
    "ods": ["pdf", "xlsx"],
    "odp": ["pdf", "pptx"],
    "rtf": ["pdf", "docx"],
    "txt": ["pdf", "docx"],
}


class ConversionError(RuntimeError):
    pass


def get_targets_for(extension: str) -> list[str]:
    return EXTENSION_TARGETS.get(extension.lower(), [])


def convert_file(source_path: Path, target_format: str) -> Path:
    """
    Converts source_path to target_format using LibreOffice headless mode.
    Returns the path to the converted file. Raises ConversionError on failure.
    """
    job_dir = source_path.parent
    cmd = [
        "soffice",
        "--headless",
        "--norestore",
        "--convert-to",
        target_format,
        "--outdir",
        str(job_dir),
        str(source_path),
    ]

    logger.info("Running conversion: %s", " ".join(cmd))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise ConversionError("Conversion timed out.") from exc

    if result.returncode != 0:
        logger.error("soffice failed: %s", result.stderr)
        raise ConversionError(f"Conversion failed: {result.stderr.strip()[:300]}")

    expected_output = job_dir / f"{source_path.stem}.{target_format}"
    if not expected_output.exists():
        raise ConversionError("Conversion did not produce an output file.")

    return expected_output


def make_job_dir() -> Path:
    job_dir = Path(settings.TMP_DIR) / uuid.uuid4().hex
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir
