import codecs
from pathlib import Path

from Crypto.Cipher import AES

# k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2023-04-14 07.34.00\com.tencent.mobileqq.tar"
# k_key = "95C0C992FC430DE11FF46C0D3A3860FF90CF4D0C87E4073AF774CE230DB3DA8A"
# k_iv = "A189BDC346A0CBE7ED5B9D3E3408699B"

# k_src = r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2023-04-14 08.31.17\com.tencent.mm.tar"
# k_key = "647726B1A097773C458912EDC6D943DBB11048FE51EF668CE100E36ADACF3C45"
# k_iv = "7F75F29A3A6F1D2C1CB205B77FA4618A"

k_src = r"C:\Users\barco\Nox_share\Download\his\HUAWEI P40 Pro+_2023-04-14 07.34.00\com.tencent.mobileqq#TwinApp.tar"
k_key = "95C0C992FC430DE11FF46C0D3A3860FF90CF4D0C87E4073AF774CE230DB3DA8A"
k_iv = "A189BDC346A0CBE7ED5B9D3E3408699B"


def main():
    src = Path(k_src)
    dst = src.parent / f"{src.stem}.out{src.suffix}"
    cipher = AES.new(codecs.decode(k_key, 'hex'), AES.MODE_GCM, nonce=codecs.decode(k_iv, 'hex'))
    open(dst, 'wb').write(cipher.decrypt(open(src, 'rb').read()))


if __name__ == '__main__':
    main()
