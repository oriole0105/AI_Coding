#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Format Converter (v2)
Converts CSV files based on configuration in setting.yaml
"""

import argparse
import csv
import sys
import os

def load_settings(config_file='setting.yaml'):
    """
    Load types from setting.yaml.
    Parses a simple yaml structure:
    types:
      - value1
      - value2
    """
    types = []
    if not os.path.exists(config_file):
        print(f"Warning: {config_file} not found. Using default types.")
        return ['plan', 'create', 'pass']

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            in_types = False
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('types:'):
                    in_types = True
                    continue
                
                # Check for list items
                if in_types and line.startswith('-'):
                    # Extract value after '- '
                    t = line[1:].strip()
                    if t:
                        types.append(t)
                elif in_types and not line.startswith('-'):
                    # End of types section
                    break
    except Exception as e:
        print(f"Error reading {config_file}: {e}")
        sys.exit(1)
    
    if not types:
        print("Warning: No types found in settings. Using defaults.")
        return ['plan', 'create', 'pass']
        
    return types

def read_input_data(input_file, types):
    """
    Reads the input CSV file.
    Expected format: Date, Val1, Val2, ... (matching types order)
    Returns a list of raw rows: {'date': date, 'values': {type: val, ...}}
    """
    raw_data = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            line_num = 0
            for row in reader:
                line_num += 1
                if not row: continue
                
                # Clean whitespace
                row = [x.strip() for x in row]
                
                # Basic validation
                # We expect Date + len(types) columns
                if len(row) < 1 + len(types):
                    print(f"Warning: Line {line_num} has insufficient columns. Expected {1+len(types)}, got {len(row)}. Skipping.")
                    continue
                
                date = row[0]
                values = {}
                for i, t in enumerate(types):
                    # Values start at index 1
                    if i + 1 < len(row):
                        values[t] = row[i+1]
                    else:
                        values[t] = ""
                
                raw_data.append({'date': date, 'values': values})
                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
        
    return raw_data

def generate_format1(raw_data, types):
    """
    Format 1: Group by Date (Date1-TypeA, Date1-TypeB, Date2-TypeA...)
    """
    output_rows = []
    for row in raw_data:
        date = row['date']
        for t in types:
            val = row['values'].get(t, "")
            output_rows.append([date, t, val])
    return output_rows

def generate_format2(raw_data, types):
    """
    Format 2: Group by Type (TypeA-AllDates, TypeB-AllDates...)
    """
    output_rows = []
    for t in types:
        for row in raw_data:
            date = row['date']
            val = row['values'].get(t, "")
            output_rows.append([date, t, val])
    return output_rows

def write_output_csv(output_file, rows):
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"Successfully wrote {len(rows)} rows to '{output_file}'")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='CSV Format Converter')
    parser.add_argument('-i', '--input', default='input.csv', help='Input CSV file')
    parser.add_argument('-o', '--output', default='output.csv', help='Output CSV file')
    # According to requirements: Format 2 is default
    parser.add_argument('-f', '--format', type=int, choices=[1, 2], default=2, help='Output format type (1 or 2). Default is 2.')
    
    args = parser.parse_args()
    
    # 1. Load Settings
    types = load_settings()
    print(f"Loaded types: {types}")
    
    # 2. Read Input
    print(f"Reading from {args.input}...")
    raw_data = read_input_data(args.input, types)
    
    # 3. Process Data
    if args.format == 1:
        print("Converting to Format 1 (Group by Date)...")
        output_rows = generate_format1(raw_data, types)
    else:
        print("Converting to Format 2 (Group by Type)...")
        output_rows = generate_format2(raw_data, types)
        
    # 4. Write Output
    write_output_csv(args.output, output_rows)

if __name__ == "__main__":
    main()
