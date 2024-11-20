import hashlib
import json
import os
import uuid
from os import PathLike
from typing import Union


def get_uuid(file: Union[str, bytes, PathLike], chunk_size: int = 8192) -> str:
    """
    根据文件内容生成 UUID，支持自动类型检测和分块计算哈希值。
    :param file: 文件内容，可以是 bytes（直接的文件内容）或 str（文件路径）
    :param chunk_size: 分块读取大小，默认为 8192 字节
    :return: 基于文件内容生成的 UUID
    """
    hash_func = hashlib.sha256()  # 使用 SHA256 哈希算法
    if isinstance(file, bytes):
        hash_func.update(file)
    elif isinstance(file, str) or isinstance(file, PathLike):
        with open(file, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
    else:
        raise ValueError("Unsupported input type. Must be 'bytes' or 'str'.")
    file_hash = hash_func.hexdigest()
    return str(uuid.UUID(file_hash[:32]))

def get_initial_assets():
    # TODO: Delete After Implementing the AssetsDatabase class
    with open(os.path.join(os.path.dirname(__file__), "assets", "initial_assets.json"), "r") as f:
        return json.load(f)