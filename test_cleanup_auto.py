#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化关机清理功能测试脚本

测试清理服务能否正确清除路由器账号密码
"""

import sys
import os
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 添加site-packages路径
site_packages = r"C:\Program Files\Python311\Lib\site-packages"
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

import logging
from shutdown_cleanup_service import RouterAccountCleaner

def setup_logging():
    """设置日志"""
    log_dir = Path(r"C:\Program Files\TPLinkDialer\logs")
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except:
        log_dir = Path(os.environ.get('TEMP', '/tmp')) / 'tplink_cleanup'
        log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / 'test_cleanup.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8', mode='a'),
            logging.StreamHandler()
        ],
        force=True
    )

    return logging.getLogger(__name__)

def main():
    """主测试函数"""
    logger = setup_logging()

    logger.info("=" * 60)
    logger.info("开始关机清理功能测试")
    logger.info("=" * 60)

    try:
        # 创建清理器
        logger.info("正在创建RouterAccountCleaner...")
        cleaner = RouterAccountCleaner()
        logger.info(f"RouterAccountCleaner创建成功 (路由器: {cleaner.router_ip})")

        # 执行清理
        logger.info("\n开始执行清理操作...")
        success = cleaner.clear_account()

        logger.info("\n" + "=" * 60)
        if success:
            logger.info("测试成功：账号密码已清除")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("测试失败：账号密码清除失败")
            logger.error("=" * 60)
            return 1

    except Exception as e:
        logger.error(f"测试过程出错: {e}", exc_info=True)
        logger.error("=" * 60)
        return 1

if __name__ == '__main__':
    exit(main())
