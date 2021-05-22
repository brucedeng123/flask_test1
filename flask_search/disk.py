import os
import os.path as pt


def scan_file(path):
    result = []
    for root, dirs, files in os.walk(path):
        for f in files:
            file_path = pt.abspath(pt.join(root, f))

            result.append((file_path, file_path[0]))  # 保存路径与盘符

    return result