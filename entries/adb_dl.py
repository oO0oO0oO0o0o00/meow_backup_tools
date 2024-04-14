""" Download media folders through ADB. """
from adb.meow_bak import do

if __name__ == '__main__':
    do("240414", [
        "/sdcard/DCIM",
        "/sdcard/Download",
        "/sdcard/Movies",
        "/sdcard/Pictures",
        "/sdcard/Recordings",
        "/sdcard/Sounds",
        "/sdcard/Tencent/QQ_Images",
        # "/sdcard/Android/data/com.tencent.mm/MicroMsg/Download",
        # "/sdcard/Android/data/com.tencent.mobileqq/Tencent/QQfile_recv",
    ], r"C:\Users\barco\Documents\HiSuite\backup\HUAWEI P40 Pro+_2024-04-13 18.38.35\storage", excludes=[".*"])