import codecs
from pathlib import Path

from Crypto.Cipher import AES
from loguru import logger

# k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2023-04-14 07.34.00\com.tencent.mobileqq.tar"
# k_key = "95C0C992FC430DE11FF46C0D3A3860FF90CF4D0C87E4073AF774CE230DB3DA8A"
# k_iv = "A189BDC346A0CBE7ED5B9D3E3408699B"

# k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2023-04-14 08.31.17\com.tencent.mm.tar"
# k_key = "647726B1A097773C458912EDC6D943DBB11048FE51EF668CE100E36ADACF3C45"
# k_iv = "7F75F29A3A6F1D2C1CB205B77FA4618A"

k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2023-10-05 12.44.29\com.tencent.mm_appDataTar\main\com.tencent.mm.tar.1"
k_key = "2E686DC6509A6A64DEDFE35A334EC24CF734C7F751C0DFAEF5A84617A160A51A"
k_iv = "F135B59A69D0AE876668E2A39903F57C"
k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2023-10-05 12.44.29\com.tencent.mm_appDataTar"


def main():
    src_root = Path(k_src)
    if src_root.is_dir():
        dst_root = Path(k_src) / "out"
        dst_root.mkdir(exist_ok=True)
        for src in Path(k_src).glob("*.tar"):
            process_file(src, dst_root / src.name)
    else:
        src = src_root
        dst = src.parent / f"{src.stem}.out{src.suffix}"
        process_file(src, dst)


def process_file(src: Path, dst: Path):
    logger.info(f"Processing {src.name}.")
    cipher = AES.new(codecs.decode(k_key, 'hex'), AES.MODE_GCM, nonce=codecs.decode(k_iv, 'hex'))
    open(dst, 'wb').write(cipher.decrypt(open(src, 'rb').read()))


if __name__ == '__main__':
    main()
