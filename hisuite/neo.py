import codecs
from pathlib import Path

from Crypto.Cipher import AES
from loguru import logger

k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro_2024-12-15 12.57.51\com.tencent.mobileqq#TwinApp.tar"
k_key = "D4412A311A2F7466B49A338572F8F37AAA0051771F7E14E950F08D129FBBE40D"
k_iv = "44DB4E4C90EA82879045FCDDCE258207"


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
