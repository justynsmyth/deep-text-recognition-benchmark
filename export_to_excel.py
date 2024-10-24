import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill
import re

data = {}
highlighted_cells = {}

input_file_path = "/Users/jiyuchen/Documents/MDP/deep-text-recognition-benchmark/infer_result.txt"

with open(input_file_path, "r") as file:
    for line in file:
        line = line.strip()
        
        parts = line.split()
        
        match = re.match(r'test_data/(stack_\d+)_.*', parts[0])
        if match:
            stack_prefix = match.group(1)
            
            if stack_prefix not in data:
                data[stack_prefix] = []
                highlighted_cells[stack_prefix] = []
            
            try:
                value = float(parts[2])
                if value > 0.95:
                    data[stack_prefix].append(parts[1])
                else:
                    data[stack_prefix].append(parts[1])
                    highlighted_cells[stack_prefix].append(len(data[stack_prefix]) - 1)
            except ValueError:
                print(f"Could not convert {parts[2]} to float.")

max_columns = max(len(values) for values in data.values())

for key in data:
    data[key].extend([''] * (max_columns - len(data[key])))

df = pd.DataFrame.from_dict(data, orient='index')

columns = []
for i in range(max_columns):
    columns.append(f"Label_{i+1}")

df.columns = columns

output_file_path = "/Users/jiyuchen/Documents/MDP/deep-text-recognition-benchmark/output.xlsx"

df.to_excel(output_file_path, index_label="StackPrefix")

wb = openpyxl.load_workbook(output_file_path)
ws = wb.active

highlight_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

for stack_prefix, columns_to_highlight in highlighted_cells.items():
    row_idx = df.index.get_loc(stack_prefix) + 2  
    for col_idx in columns_to_highlight:
        excel_column = col_idx + 2 
        ws.cell(row=row_idx, column=excel_column).fill = highlight_fill

wb.save(output_file_path)

print(f"Data has been successfully written to {output_file_path}")