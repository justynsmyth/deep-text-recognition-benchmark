import os
import argparse


def parse_inference_file(inference_file, output_file):
    output_lines = []

    # Read the file in binary mode to avoid encoding issues
    with open(inference_file, 'rb') as file:
        for line in file:
            # Decode the line and replace null characters
            clean_line = line.decode('latin-1').replace('\x00', '').strip()
            
            # Skip dashed lines and irrelevant headers
            if clean_line.startswith('-') or "image_path" in clean_line:
                continue

            parts = clean_line.split('\t')
            if len(parts) >= 2:
                image_path = parts[0].strip()
                image_name = os.path.basename(image_path)  # Extract filename
                predicted_label = parts[1].strip()
                output_lines.append(f"{image_name}\t{predicted_label}\n")

    write_gt_file(output_lines, output_file)

def write_gt_file(output_lines, gt_file):
    with open(gt_file, 'w', encoding='utf-8') as file:
        for line in output_lines:
            file.write(line)

# Usage Example
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process inference file.")
    parser.add_argument("inference_file", type=str, help="Path to the inference file")
    parser.add_argument("--output", type=str, default="gt_inference.txt", help="Path to the output file (default: gt_inference.txt)")

    args = parser.parse_args()

    inference_file = 'compare.txt'
    output_file = 'gt.txt'
    parse_inference_file(args.inference_file, args.output)
    print(f"GT file created at {output_file}")