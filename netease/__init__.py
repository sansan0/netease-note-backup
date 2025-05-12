"""网易云音乐动态备份工具"""

from .version import __version__

__all__ = ['__version__']

import sys
import io
import os

# 全局处理无控制台输出的问题
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()
        
    # 禁用 Playwright 的控制台输出
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'
    os.environ['DEBUG'] = '0'