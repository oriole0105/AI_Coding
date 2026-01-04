#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV格式轉換程式
將輸入的CSV檔案轉換為指定的輸出格式
"""

import argparse
import csv
import sys


def read_input_csv(filename):
    """
    讀取輸入的CSV檔案    
    Args:
        filename: 輸入檔案名稱
    Returns:
        list: 包含所有資料行的列表，每行為 [date, plan, create, pass]
    """
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    # 去除空白並轉換數值
                    date = row[0].strip()
                    plan = row[1].strip()
                    create = row[2].strip()
                    pass_val = row[3].strip()
                    data.append([date, plan, create, pass_val])
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 '{filename}'")
        sys.exit(1)
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
        sys.exit(1)
    
    return data


def convert_to_format1(data):
    """
    轉換為格式1: 日期, type, 數值
    Args:
        data: 輸入資料列表
    Returns:
        list: 轉換後的資料列表
    """
    result = []
    for row in data:
        date, plan, create, pass_val = row
        result.append([date, 'plan', plan])
        result.append([date, 'create', create])
        result.append([date, 'pass', pass_val])
    return result


def convert_to_format2(data):
    """
    轉換為格式2: type, 日期, 數值
    按type分組排列
    Args:
        data: 輸入資料列表 
    Returns:
        list: 轉換後的資料列表
    """
    result = []
    
    # 先收集所有plan的資料
    for row in data:
        date, plan, _, _ = row
        result.append(['plan', date, plan])
    
    # 再收集所有create的資料
    for row in data:
        date, _, create, _ = row
        result.append(['create', date, create])
    
    # 最後收集所有pass的資料
    for row in data:
        date, _, _, pass_val = row
        result.append(['pass', date, pass_val])
    
    return result


def write_output_csv(filename, data):
    """
    寫入輸出的CSV檔案
    
    Args:
        filename: 輸出檔案名稱
        data: 要寫入的資料列表
    """
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
        print(f"成功將資料寫入 '{filename}'")
    except Exception as e:
        print(f"寫入檔案時發生錯誤: {e}")
        sys.exit(1)


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='CSV格式轉換程式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python csv_formatter.py -i input.csv -o output.csv
  python csv_formatter.py -i input.csv -o output.csv -f 1
  python csv_formatter.py -f 2
        """
    )
    
    parser.add_argument('-i', '--input', 
                        default='input.csv',
                        help='輸入檔案名稱 (預設: input.csv)')
    
    parser.add_argument('-o', '--output',
                        default='output.csv',
                        help='輸出檔案名稱 (預設: output.csv)')
    
    parser.add_argument('-f', '--format',
                        type=int,
                        choices=[1, 2],
                        default=2,
                        help='輸出格式 (1 或 2, 預設: 2)')
    
    args = parser.parse_args()
    
    # 顯示處理資訊
    print(f"讀取檔案: {args.input}")
    print(f"輸出檔案: {args.output}")
    print(f"輸出格式: format{args.format}")
    print("-" * 50)
    
    # 讀取輸入檔案
    data = read_input_csv(args.input)
    
    if not data:
        print("警告: 輸入檔案沒有資料")
        sys.exit(1)
    
    print(f"讀取到 {len(data)} 筆資料")
    
    # 根據指定的格式轉換資料
    if args.format == 1:
        output_data = convert_to_format1(data)
    else:
        output_data = convert_to_format2(data)
    
    # 寫入輸出檔案
    write_output_csv(args.output, output_data)


if __name__ == '__main__':
    main()