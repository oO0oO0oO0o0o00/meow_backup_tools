"""Test the time taken to hash large files."""
import hashlib
import time
from random import randbytes


def run():
    md5 = hashlib.md5()
    for _ in range(50):
        md5.update(randbytes(1024 * 1024 * 10))
    return md5.hexdigest()


def main():
    print(timeit(run))


def timeit(fn):
    t = time.time()
    fn()
    return time.time() - t


if __name__ == '__main__':
    main()
