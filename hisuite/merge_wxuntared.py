import argparse
import glob
import os
import shutil
from os.path import join as pjoin
from pathlib import Path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Synchronize a directory between an Android device and the '
                    'local file system')
    parser.add_argument(
        'home',
        metavar='/some/home/path',
        type=str,
        help='Where the MicroMsgX folders reside')
    args = parser.parse_args()

    for src_folder in glob.glob(pjoin(args.home, "*MicroMsg*/")):
        # /home/MicroMsg0
        src_folder_path = Path(src_folder)
        # MicroMsg0
        dst_folder = src_folder_path.name
        while dst_folder[-1] in "0123456789":
            # MicroMsg
            dst_folder = dst_folder[:-1]
        # /home/MicroMsg
        dst_folder = pjoin(src_folder_path.parent, dst_folder)
        os.makedirs(dst_folder, exist_ok=True)
        # /home/MicroMsg0 ['a', 'b'], ['c.txt']
        # /home/MicroMsg0/a ['a1'], ['aaa.jpg']
        for src_current_parent, src_component_folders, src_component_files in \
                os.walk(src_folder, topdown=True):
            # build path: /home/MicroMsg0/a -> /home/MicroMsg/a
            dst_current_parent = pjoin(dst_folder, os.path.relpath(src_current_parent, src_folder))
            print(src_current_parent, src_component_folders, src_component_files)
            # if we could move a folder as a whole, then no need to walk into it
            removes = []
            # 'a' in ['a', 'b']
            for component_folder_name in src_component_folders:
                # /home/MicroMsg/a
                dst_component_folder = pjoin(dst_current_parent, component_folder_name)
                # if /home/MicroMsg/a does not exist then we can move /home/MicroMsg0/a as a whole
                if not os.path.exists(dst_component_folder):
                    # move folder: /home/MicroMsg0/a -> /home/MicroMsg/a
                    shutil.move(pjoin(src_current_parent, component_folder_name), dst_component_folder)
                    # remember to remove to from the walking list because we are done with it
                    removes.append(component_folder_name)
            # remove moved folders from the walking list
            for rem in removes:
                src_component_folders.remove(rem)
            # regular files, just move, no conflicts in this use case
            for compoment_file_name in src_component_files:
                shutil.move(pjoin(src_current_parent, compoment_file_name),
                            pjoin(dst_current_parent, compoment_file_name))
