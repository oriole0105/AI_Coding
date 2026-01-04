#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Format Converter (v4)
Converts CSV files based on configuration in setting.yaml
Appends processed milestone data to the output.
Can generate an AsciiDoc file with embedded Vega-Lite chart.
"""

import argparse
import csv
import sys
import os
import json

def load_settings(config_file='setting.yaml'):
    """
    Load types from setting.yaml.
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
                
                row = [x.strip() for x in row]
                
                if len(row) < 1 + len(types):
                    print(f"Warning: Line {line_num} has insufficient columns. Expected {1+len(types)}, got {len(row)}. Skipping.")
                    continue
                
                date = row[0]
                values = {}
                for i, t in enumerate(types):
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

def get_max_value(raw_data):
    """
    Calculates the maximum integer value across all types in the input data.
    """
    max_val = 0
    for row in raw_data:
        for val in row['values'].values():
            try:
                # Handle empty strings or non-numeric
                if val:
                    int_val = int(val)
                    if int_val > max_val:
                        max_val = int_val
            except ValueError:
                continue
    return max_val

def read_milestones(milestone_file):
    """
    Reads the milestone CSV file.
    Expected format: Date, Name
    Returns a list of tuples: (Date, Name)
    """
    milestones = []
    if not os.path.exists(milestone_file):
        print(f"Warning: Milestone file '{milestone_file}' not found. Skipping milestones.")
        return milestones

    try:
        with open(milestone_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    date = row[0].strip()
                    name = row[1].strip()
                    milestones.append((date, name))
    except Exception as e:
        print(f"Error reading milestone file: {e}")
        
    return milestones

def generate_format1(raw_data, types):
    output_rows = []
    for row in raw_data:
        date = row['date']
        for t in types:
            val = row['values'].get(t, "")
            output_rows.append([date, t, val])
    return output_rows

def generate_format2(raw_data, types):
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

def generate_adoc(adoc_file, rows):
    """
    Generates an AsciiDoc file with an embedded Vega-Lite chart using inline data.
    """
    # Convert CSV rows to list of dicts for JSON
    json_values = []
    for row in rows:
        # row format: [date, type, value, (optional) milestone]
        item = {
            "date": row[0],
            "type": row[1],
            "value": int(row[2]) if str(row[2]).isdigit() else 0
        }
        if len(row) > 3:
            item["milestone"] = row[3]
        json_values.append(item)

    vegalite_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "Combined Line and Bar Chart with Milestones",
        "width": 600,
        "height": 400,
        "data": {
            "values": json_values
        },
        "layer": [
            {
                "description": "Line chart for plan, create, pass",
                "transform": [
                    {"filter": "datum.type != 'bar'"}
                ],
                "mark": {"type": "line", "point": True},
                "encoding": {
                    "x": {
                        "field": "date", 
                        "type": "temporal", 
                        "title": "Date (Time)"
                    },
                    "y": {
                        "field": "value", 
                        "type": "quantitative", 
                        "title": "Value"
                    },
                    "color": {
                        "field": "type", 
                        "type": "nominal", 
                        "title": "Type",
                        "scale": {"scheme": "category10"}
                    }
                }
            },
            {
                "description": "Bar chart for milestones",
                "transform": [
                    {"filter": "datum.type == 'bar'"}
                ],
                "mark": {"type": "bar", "width": 2, "color": "red", "opacity": 0.7},
                "encoding": {
                    "x": {"field": "date", "type": "temporal"},
                    "y": {"field": "value", "type": "quantitative"}
                }
            },
            {
                "description": "Text labels for milestones",
                "transform": [
                    {"filter": "datum.type == 'bar'"}
                ],
                "mark": {"type": "text", "align": "center", "baseline": "bottom", "dy": -5, "color": "black"},
                "encoding": {
                    "x": {"field": "date", "type": "temporal"},
                    "y": {"field": "value", "type": "quantitative"},
                    "text": {"field": "milestone", "type": "nominal"}
                }
            }
        ]
    }

    adoc_content = f"""[vegalite]
----
{json.dumps(vegalite_spec, indent=2)}
----
"""
    
    try:
        with open(adoc_file, 'w', encoding='utf-8') as f:
            f.write(adoc_content)
        print(f"Successfully wrote AsciiDoc report to '{adoc_file}'")
    except Exception as e:
        print(f"Error writing AsciiDoc file: {e}")

def main():
    parser = argparse.ArgumentParser(description='CSV Format Converter')
    parser.add_argument('-i', '--input', default='input.csv', help='Input CSV file')
    parser.add_argument('-o', '--output', default='output.csv', help='Output CSV file')
    parser.add_argument('-f', '--format', type=int, choices=[1, 2], default=2, help='Output format type (1 or 2). Default is 2.')
    parser.add_argument('-m', '--milestone', default='milestone.csv', help='Milestone CSV file')
    parser.add_argument('-a', '--adoc', help='Output AsciiDoc file path (optional)')
    
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
    
    # 4. Process Milestones
    print(f"Reading milestones from {args.milestone}...")
    milestones = read_milestones(args.milestone)
    
    if milestones:
        max_val = get_max_value(raw_data)
        milestone_val = max_val + 10
        print(f"Max value in input: {max_val}. Milestone value: {milestone_val}")
        
        for date, name in milestones:
            # Format: Date, "bar", Value, Name
            output_rows.append([date, 'bar', milestone_val, name])
    
    # 5. Write Output CSV
    write_output_csv(args.output, output_rows)

    # 6. Write AsciiDoc if requested
    if args.adoc:
        generate_adoc(args.adoc, output_rows)

if __name__ == "__main__":
    main()
