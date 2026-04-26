from collections import namedtuple
from pathlib import Path
from uuid import uuid4

from loguru import logger

from settings.settings import app_settings


async def scan_folder_cache(folder: Path = app_settings.target_folder) -> list:
    """
    Scan folder and get list for working like cache
    :param folder:
    :return:
    """
    if not folder.exists():
        logger.error("Target folder not found")
    Files_tuple = namedtuple("Files_tuple", ["name", "path", "id"])

    return [
        Files_tuple(f.name, f.absolute(), str(uuid4())[:8])
        for f in folder.rglob("*.xlsx")
    ]


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
