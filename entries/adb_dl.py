""" Download media folders through ADB. """
from adb.meow_bak import do

if __name__ == '__main__':
    do("250111", 60, [
        "1",
        "DCIM",
        "Download",
        "EditedOnlinePhotos",
        "Movies",
        "Pictures",
        # "Recordings",
        "Sounds",
        # "Tencent/QQ_Images",
        # "Android/data/com.tencent.mm/MicroMsg/Download",
        # "Android/data/com.tencent.mobileqq/Tencent/QQfile_recv",
    ], r"C:\Users\barco\bak_tmp", excludes=[".*"])
    # do("250111", 10, [
    #     "/sdcard/alipay",
    # ], r"C:\Users\barco\Documents\HiSuite\backup\250111\test", excludes=[".*"])
