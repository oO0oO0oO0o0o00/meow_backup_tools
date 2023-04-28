from pathlib import Path

from archives.build_archives import build_archives_for_years

if __name__ == '__main__':
    # build_archives_for_projects(
    #     Path(r"F:\LOFL\before-2015"),
    #     Path(r"G:\LOAR\before-2015")
    # )
    build_archives_for_years(
        Path(r"F:\LOFL\before-2015"),
        Path(r"G:\LOAR\before-2015")
    )
