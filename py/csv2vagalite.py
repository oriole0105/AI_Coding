#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將 Format2 CSV 檔案轉換為 Kroki 可用的 Vega-Lite JSON
"""

import argparse
import csv
import json
import sys


def read_csv_format2(filename):
    """
    讀取 Format2 CSV 檔案
    Format2: type, date, value
    
    Args:
        filename: CSV 檔案名稱
        
    Returns:
        list: 資料列表，格式為 [{"type": ..., "date": ..., "value": ...}, ...]
    """
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    type_val = row[0].strip()
                    date_val = row[1].strip()
                    value_val = float(row[2].strip())
                    
                    data.append({
                        "type": type_val,
                        "date": date_val,
                        "value": value_val
                    })
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 '{filename}'")
        sys.exit(1)
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
        sys.exit(1)
    
    return data


def generate_vegalite_spec(data, title="CSV Data Trend Analysis", width=800, height=400):
    """
    生成 Vega-Lite JSON 規格
    
    Args:
        data: 資料列表
        title: 圖表標題
        width: 圖表寬度
        height: 圖表高度
        
    Returns:
        dict: Vega-Lite 規格
    """
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {
            "text": title,
            "fontSize": 18,
            "fontWeight": "bold"
        },
        "description": "Line chart showing plan, create, and pass metrics over time",
        "width": width,
        "height": height,
        "data": {
            "values": data
        },
        "mark": {
            "type": "line",
            "point": {
                "filled": True,
                "size": 100
            },
            "strokeWidth": 3
        },
        "encoding": {
            "x": {
                "field": "date",
                "type": "temporal",
                "title": "Date",
                "axis": {
                    "labelAngle": -45,
                    "labelFontSize": 11,
                    "titleFontSize": 13,
                    "format": "%Y-%m-%d",
                    "grid": True
                }
            },
            "y": {
                "field": "value",
                "type": "quantitative",
                "title": "Quantity",
                "axis": {
                    "labelFontSize": 11,
                    "titleFontSize": 13,
                    "grid": True
                },
                "scale": {
                    "zero": True,
                    "nice": True
                }
            },
            "color": {
                "field": "type",
                "type": "nominal",
                "title": "Type",
                "scale": {
                    "domain": ["plan", "create", "pass"],
                    "range": ["#1f77b4", "#ff7f0e", "#2ca02c"]
                },
                "legend": {
                    "orient": "top-right",
                    "title": "Type",
                    "titleFontSize": 13,
                    "labelFontSize": 12,
                    "symbolSize": 100,
                    "symbolStrokeWidth": 3
                }
            },
            "tooltip": [
                {
                    "field": "date",
                    "type": "temporal",
                    "title": "Date",
                    "format": "%Y-%m-%d"
                },
                {
                    "field": "type",
                    "type": "nominal",
                    "title": "Type"
                },
                {
                    "field": "value",
                    "type": "quantitative",
                    "title": "Quantity"
                }
            ]
        },
        "config": {
            "view": {
                "strokeWidth": 0
            }
        }
    }
    
    return spec


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='將 Format2 CSV 轉換為 Kroki 可用的 Vega-Lite JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python csv_to_vegalite.py -i output.csv -o chart.json
  python csv_to_vegalite.py -i output.csv -o chart.json -t "My Chart" -w 1000 -h 500
        """
    )
    
    parser.add_argument('-i', '--input',
                        required=True,
                        help='輸入 CSV 檔案 (Format2)')
    
    parser.add_argument('-o', '--output',
                        default='chart_spec.json',
                        help='輸出 JSON 檔案 (預設: chart_spec.json)')
    
    parser.add_argument('-t', '--title',
                        default='CSV Data Trend Analysis',
                        help='圖表標題')
    
    parser.add_argument('-w', '--width',
                        type=int,
                        default=800,
                        help='圖表寬度 (預設: 800)')
    
    parser.add_argument('-ht', '--height',
                        type=int,
                        default=400,
                        help='圖表高度 (預設: 400)')
    
    parser.add_argument('--compact',
                        action='store_true',
                        help='輸出壓縮的 JSON (無縮排)')
    
    args = parser.parse_args()
    
    # 讀取 CSV
    print(f"讀取 CSV 檔案: {args.input}")
    data = read_csv_format2(args.input)
    
    if not data:
        print("錯誤: 沒有讀取到任何資料")
        sys.exit(1)
    
    print(f"成功讀取 {len(data)} 筆資料")
    
    # 生成 Vega-Lite 規格
    spec = generate_vegalite_spec(data, args.title, args.width, args.height)
    
    # 寫入 JSON
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.compact:
                json.dump(spec, f, ensure_ascii=False)
            else:
                json.dump(spec, f, ensure_ascii=False, indent=2)
        
        print(f"成功寫入 Vega-Lite JSON: {args.output}")
        print("\n使用方式:")
        print(f"1. 在 AsciiDoc 中使用 Kroki 區塊")
        print(f"2. 或在 Vega Editor 中開啟: https://vega.github.io/editor/")
        
    except Exception as e:
        print(f"寫入檔案時發生錯誤: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()