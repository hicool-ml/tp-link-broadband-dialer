#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP-Link路由器关机清理程序
独立可执行版本，配合任务计划使用
"""

import sys
import logging
from pathlib import Path


def setup_logging():
    """设置日志"""
    log_dir = Path("C:/ProgramData/BroadbandDialer")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "cleanup_http.log"  # 使用独立的日志文件

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )

    return logging.getLogger(__name__)


def main():
    """主函数"""
    logger = setup_logging()
    logger.info("=== 开始执行关机清理 ===")

    try:
        from config_manager import ConfigManager
        from tplink_http_cleaner import TPLinkHTTPCleaner

        config = ConfigManager().get_config()

        router_ip = config.get("router_ip", "192.168.1.1")
        password = config.get("router_password")

        if not password:
            logger.warning("未配置密码，跳过清理")
            return

        logger.info(f"路由器IP: {router_ip}")

        cleaner = TPLinkHTTPCleaner(router_ip, password)
        success = cleaner.run_cleanup()

        if success:
            logger.info("清理成功")
        else:
            logger.error("清理失败")

    except Exception as e:
        import traceback
        logger.error(f"执行异常: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
