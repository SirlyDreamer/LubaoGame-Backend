import hashlib
import json
import os
import uuid
from os import PathLike
from typing import Union
import mimetypes
import base64


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

def base64_decode(base64_str):
    """
    判断 base64 字符串的类型（image/audio）并解码
    :param base64_str: 输入的 base64 字符串
    :return: 文件类型（image/audio），文件数据（字节流）
    """
    try:
        # 分离头部信息和数据部分
        if "," in base64_str:
            header, data = base64_str.split(',', 1)
        else:
            raise ValueError("Invalid base64 format")

        # 从头部信息提取 MIME 类型
        mime_type = header.split(";")[0].replace("data:", "")
        file_type = mimetypes.guess_type(f"dummy.{mime_type.split('/')[1]}")[0]

        # 判别类型
        if "image" in mime_type:
            file_type = "image"
        elif "audio" in mime_type:
            file_type = "audio"
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

        # 解码数据部分
        decoded_data = base64.b64decode(data)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 string: {e}")
    finally:
        return file_type, decoded_data