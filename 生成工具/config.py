import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Config:
    """配置类"""
    # IAM认证相关
    IAM_URL: str = "https://iam-apigateway-proxy.cn-avicasgt-1.avicasgt.com/v3/auth/tokens"
    USERNAME: str = "fanhailong"
    PASSWORD: str = "Fhl1982,"
    DOMAIN_NAME: str = "avicasgt-team"
    PROJECT_ID: str = "3f0e944126fc40488b99174119ef90c9"
    
    # 通用配置
    TIMEOUT: int = 30

    
    # Token相关（运行时设置）
    #token: str = field(default="", init=False)
    #has_token: bool = field(default=False, init=False)
    token: str = field(default="MIID+AYJKoZIhvcNAQcCoIID6TCCA+UCAQExDTALBglghkgBZQMEAgEwggHGBgkqhkiG9w0BBwGgggG3BIIBs3sidG9rZW4iOnsiZXhwaXJlc19hdCI6IjIwMjUtMTItMDZUMDA6MjY6MzEuNTg2MDAwWiIsIm1ldGhvZHMiOlsicGFzc3dvcmQiXSwiY2F0YWxvZyI6W10sInJvbGVzIjpbXSwicHJvamVjdCI6eyJkb21haW4iOnsibmFtZSI6ImF2aWNhc2d0LXRlYW0iLCJpZCI6IjlhZTc2NGVkNTk3ZTQwZGViNWI4MDBhYTk5NDMxNjk1In0sIm5hbWUiOiJjbi1hdmljYXNndC0xIiwiaWQiOiIzZjBlOTQ0MTI2ZmM0MDQ4OGI5OTE3NDExOWVmOTBjOSJ9LCJpc3N1ZWRfYXQiOiIyMDI1LTEyLTA1VDAwOjI2OjMxLjU4NjAwMFoiLCJ1c2VyIjp7ImRvbWFpbiI6eyJuYW1lIjoiYXZpY2FzZ3QtdGVhbSIsImlkIjoiOWFlNzY0ZWQ1OTdlNDBkZWI1YjgwMGFhOTk0MzE2OTUifSwibmFtZSI6ImZhbmhhaWxvbmciLCJpZCI6ImRiMjMxMzAwNGQ1YzQ5MTJiMGE2MTYzOTliNDczMTllIn19fTGCAgUwggIBAgEBMFwwVjELMAkGA1UEBhMCQ04xCzAJBgNVBAgMAnNjMQswCQYDVQQHDAJjZDELMAkGA1UECgwCSFcxEDAOBgNVBAsMB0Nsb3VkQlUxDjAMBgNVBAMMBXRva2VuAgIQADALBglghkgBZQMEAgEwDQYJKoZIhvcNAQEBBQAEggGAYDDuTZoaYCkHOFdRaC4JXpHzWZu5m2ILUf7mGIWRU05TqXtLZOB7Bje1xaaZNV1gmduU2x3D3KSdnWZ1oyvkoLL+5YGr3w6+1CW766FOVznCNT7KX1HuHmd2xWbVUV0P4z-yCPqlBWpZt3t5scOWnoB45sbkvunoUM40PrwHe6z2R6WCdc8+3XS5BFwRNslXDsk2fgRrimyNgNILRvk-BM618BarRvoc5DCT-pi-IlFZ2q64RjHPZbuWPpYojvgo8PYole5L8C1c0qWcekrVdaoibT0Ix4cTAZ4QbqWN7XS4fRXJp3ngvzRzPQf0rG-1hHVzcr6SIppkW0n4CScREoFugHwyXjZAHWE15OvCJZpCuIF6lzLKHTVk4WIZCtLZF7fZ-zvK6jKf7eA-6rjRME6qTXLcqTc8aaMH87mG59SdOzwTiSr6znzftUWHfS20sqmcglu-JhQYt49s3Yiiwq9pO8XAFoKcWjdNU+kxLDUAncw0SOK0m3mHkV81vZyq", init=False)
    has_token: bool = field(default=True, init=False)
    

    #IPD
    SF_KEYWORD: str = "uCOS-III"
    IPD_TREE_URL: str = "https://codeartsreq.cn-avicasgt-1.avicasgt.com/v1/ipdprojectservice/projects/6c9fff785268446bab66073c5bc1fa56/issues/tree"
    IPD_LIST_URL: str = "https://codeartsreq.cn-avicasgt-1.avicasgt.com/v1/ipdprojectservice/projects/6c9fff785268446bab66073c5bc1fa56/issues/query"
    IPD_DETAIL_URL: str = "https://codeartsreq.cn-avicasgt-1.avicasgt.com/v1/ipdprojectservice/projects/6c9fff785268446bab66073c5bc1fa56/issues/"

    # 测试用例
    EXECUTION_TYPE_ID: int = 10005
    TC_DETAIL_URL: str = "https://codeartstestplan.cn-avicasgt-1.avicasgt.com/v1/projects/6c9fff785268446bab66073c5bc1fa56/testcase"
    TC_ALL_URL: str = "https://codeartstestplan.cn-avicasgt-1.avicasgt.com/v1/6c9fff785268446bab66073c5bc1fa56/testcases/batch-query"

    #html文件目录
    BASE_DIR_NAME: str = "verifymaterial"
    REQ_DIR_NAME: str = "requirement"

# 全局配置实例
config = Config()

def calculate_relative_path(from_path: str, to_path: str) -> str:
    """
    计算两个文件路径之间的相对路径（公共函数）

    Args:
        from_path: 源文件路径 (通常是一个文件的路径，如 `SF.html`)
        to_path: 目标文件路径 (需要链接到的文件，如 `SF描述.html`)

    Returns:
        相对路径字符串，如果路径无效则返回空字符串
    """
    if not from_path or not to_path:
        return ""

    try:
        # 1. 确定计算的起始目录
        # 如果 from_path 看起来像一个文件（有后缀），则取其所在目录[citation:6][citation:7]
        if os.path.splitext(from_path)[1]:  # 检查是否有文件扩展名
            start_dir = os.path.dirname(from_path)
        else:
            start_dir = from_path

        # 如果目录为空（例如文件在根目录），设为当前目录
        if not start_dir:
            start_dir = '.'

        # 2. 使用 os.path.relpath 计算相对路径[citation:1][citation:6][citation:8]
        # 它能够自动处理需要向上（使用 ".."）导航的情况
        relative_path = os.path.relpath(to_path, start=start_dir)

        # 3. (可选) 将Windows的反斜杠转换为正斜杠，以适应HTML和跨平台需求
        relative_path = relative_path.replace('\\', '/')

        return relative_path

    except Exception as e:
        # 捕获所有可能的异常，例如路径在不同驱动器上[citation:2]
        print(f"计算相对路径时出错 from='{from_path}', to='{to_path}': {e}")
        # 返回一个安全的回退值，例如目标路径本身或空字符串
        return ""