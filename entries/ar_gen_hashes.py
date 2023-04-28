"Generate "

from pathlib import Path

from archives import hash_archives

if __name__ == '__main__':
    hash_archives.process_tree(
        Path(r"G:\LOAR"),
        hash_archives.generate_hash
    )