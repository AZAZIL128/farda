#!/usr/bin/env python
"""نقطه ورود دستورات مدیریتی جنگو برای پروژه ایران فردا."""
import os
import sys

if __name__ == "__main__":
    # تنظیم نام ماژول تنظیمات پیش از اجرای هر دستور مدیریتی
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
