#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
获取完整HTML用于分析
"""

import requests
from pathlib import Path


def get_full_html():
    """获取完整HTML"""

    router_ip = "192.168.1.1"
    base_url = f"http://{router_ip}"

    print(f"正在访问: {base_url}/")
    print()

    session = requests.Session()
    r = session.get(base_url + "/", timeout=10)

    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print()
    print("=" * 60)
    print("完整HTML内容:")
    print("=" * 60)

    # 保存到文件
    output_file = Path("router_page.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(r.text)

    print(f"HTML已保存到: {output_file.absolute()}")
    print(f"大小: {len(r.text)} 字节")
    print()

    # 显示前1000字符
    print("前1000字符预览:")
    print(r.text[:1000])


if __name__ == '__main__':
    get_full_html()
