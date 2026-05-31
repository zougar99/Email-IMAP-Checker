#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Checker - يراقب input.txt ويشغل التحقق تلقائياً
"""

import os
import time
import subprocess
import sys
from pathlib import Path

def get_file_size(filepath):
    """الحصول على حجم الملف"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0

def get_file_lines(filepath):
    """الحصول على عدد الأسطر في الملف"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return len([l for l in f if l.strip()])
    return 0

def move_processed_lines(input_file, processed_count):
    """نقل الأسطر المعالجة إلى ملف منفصل"""
    backup_file = "input_processed.txt"
    
    if not os.path.exists(input_file):
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    if processed_count >= len(lines):
        # نقل كل الملف
        if os.path.exists(backup_file):
            with open(backup_file, 'a', encoding='utf-8') as bf:
                for line in lines:
                    bf.write(line + '\n')
        else:
            with open(backup_file, 'w', encoding='utf-8') as bf:
                for line in lines:
                    bf.write(line + '\n')
        # مسح input.txt
        with open(input_file, 'w', encoding='utf-8') as f:
            pass
    else:
        # نقل الأسطر المعالجة فقط
        processed_lines = lines[:processed_count]
        remaining_lines = lines[processed_count:]
        
        if os.path.exists(backup_file):
            with open(backup_file, 'a', encoding='utf-8') as bf:
                for line in processed_lines:
                    bf.write(line + '\n')
        else:
            with open(backup_file, 'w', encoding='utf-8') as bf:
                for line in processed_lines:
                    bf.write(line + '\n')
        
        # كتابة الأسطر المتبقية في input.txt
        with open(input_file, 'w', encoding='utf-8') as f:
            for line in remaining_lines:
                f.write(line + '\n')

def run_checker(input_file):
    """تشغيل السكريبت الرئيسي"""
    print(f"[INFO] Starting checker for {input_file}...")
    
    try:
        # تشغيل atr3.py
        result = subprocess.run(
            [sys.executable, "atr3.py", "-i", input_file],
            capture_output=True,
            text=True,
            timeout=3600  # timeout بعد ساعة
        )
        
        if result.returncode == 0:
            print("[OK] Checker completed successfully")
            return True
        else:
            print(f"[ERROR] Checker failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("[ERROR] Checker timeout")
        return False
    except Exception as e:
        print(f"[ERROR] Error running checker: {e}")
        return False

def monitor_file(input_file="input.txt", check_interval=5):
    """مراقبة الملف وتشغيل التحقق عند التغيير"""
    
    print("=" * 60)
    print("Auto Checker - Monitoring input.txt")
    print("=" * 60)
    print(f"[INFO] Monitoring: {input_file}")
    print(f"[INFO] Check interval: {check_interval} seconds")
    print(f"[INFO] Press Ctrl+C to stop")
    print("=" * 60)
    
    last_size = get_file_size(input_file)
    last_lines = get_file_lines(input_file)
    processed_lines = 0
    
    try:
        while True:
            time.sleep(check_interval)
            
            current_size = get_file_size(input_file)
            current_lines = get_file_lines(input_file)
            
            # التحقق من وجود تغييرات
            if current_size != last_size or current_lines != last_lines:
                new_lines = current_lines - last_lines
                
                if new_lines > 0:
                    print(f"\n[CHANGE] Detected {new_lines} new line(s) in {input_file}")
                    print(f"[INFO] Total lines: {current_lines}")
                    
                    # تشغيل التحقق
                    if run_checker(input_file):
                        # نقل الأسطر المعالجة
                        processed_lines = current_lines
                        move_processed_lines(input_file, processed_lines)
                        print(f"[OK] Processed {processed_lines} lines")
                        print(f"[INFO] Moved to input_processed.txt")
                    
                    # تحديث القيم
                    last_size = get_file_size(input_file)
                    last_lines = get_file_lines(input_file)
                elif current_lines < last_lines:
                    # تم حذف أسطر (ربما تمت المعالجة)
                    print(f"[INFO] File reduced: {last_lines} -> {current_lines} lines")
                    last_size = current_size
                    last_lines = current_lines
            
    except KeyboardInterrupt:
        print("\n[INFO] Stopping monitor...")
        print("[INFO] Goodbye!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Checker - Monitor input.txt')
    parser.add_argument('-i', '--input', default='input.txt', help='Input file to monitor')
    parser.add_argument('-t', '--interval', type=int, default=5, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    monitor_file(args.input, args.interval)

