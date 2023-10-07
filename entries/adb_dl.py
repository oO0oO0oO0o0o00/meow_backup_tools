""" Download media folders through ADB. """
from adb.meow_bak import do

if __name__ == '__main__':
    do("230927", [
        "/sdcard/DCIM",
        "/sdcard/documents",
        "/sdcard/Download",
        "/sdcard/Pictures",
        "/sdcard/Sounds",
        # "/sdcard/tieba",
        "/sdcard/Tencent/QQ_Images",
        "/sdcard/Tencent/QQ_Videos",
        "/sdcard/Movies",
        # "/sdcard/Tencent/MicroMsg/WeiXin",
        # "/sdcard/Android/data/com.tencent.mm/MicroMsg/Download",
        # "/sdcard/Android/data/com.tencent.mobileqq/Tencent/QQfile_recv",
    ], r"D:\phonebak\230927\storage", excludes=[".*"])