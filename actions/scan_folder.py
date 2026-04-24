from settings.settings import app_settings
from pathlib import Path
from loguru import logger


async def scan_folder(target: str, folder: Path = app_settings.target_folder) -> list:
    """
    Scan folder and return found file list
    :param target:
    :param folder:
    :return:
    """
    if not folder.exists():
        logger.error("Target folder not found")
    logger.debug(f"Scan folder {folder}")
    return [
        f
        for f in folder.rglob("*.xlsx")
        if f.is_file() and target.lower() in f.name.lower()
    ]
