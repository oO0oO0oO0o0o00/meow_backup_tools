"""Add projects (contents of "before-20xx") to local archives per-project or per-year. """

import os
import shutil
from pathlib import Path

from loguru import logger


def build_archives_for_projects(src_path: Path, dst_path: Path):
    for file in src_path.iterdir():
        # if file.is_dir() and (file.parent / f"{file.name}.zip").exists():
        #     logger.warning(file)
        _build_archives_for_project(src_path, file, dst_path)


def build_archives_for_years(src_path: Path, dst_path: Path):
    years = set()
    for file in src_path.iterdir():
        file = file.name
        assert file[4] == "-"
        years.add(int(file[:4]))
    for year in sorted(years):
        dst_file = dst_path / f"{year}.zip"
        src_files = [f"\"{str(file)}\"" for file in src_path.glob(f"{year}-*")]
        command = f"7z a \"{str(dst_file)}\" {' '.join(src_files)}"
        _run_zip_command(command)
        logger.info("Done with year {}.", year)


def _build_archives_for_project(src_root: Path, src_file: Path, dst_root: Path):
    is_dir = src_file.is_dir()
    dst_file = dst_root / f"{src_file.name}.zip" if is_dir else dst_root / src_file.name
    if dst_file.exists():
        logger.info("Skipping {}: exists.", str(src_file.relative_to(src_root)))
        return
    if is_dir:
        command = f"7z a \"{str(dst_file)}\" \"{str(src_file)}\""
        # logger.debug(command)
        _run_zip_command(command)
    else:
        shutil.move(src_file, dst_file)


def _run_zip_command(command):
    ret = os.system(command)
    if ret != 0:
        logger.error("Zip failed, return code: {}", ret)
        raise RuntimeError()
