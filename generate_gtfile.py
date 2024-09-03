def generate_gt_file(output_file):
    data = [
        ("test/demo_1.png", "Available"),
        ("test/demo_2.png", "Shakeshack"),
        ("test/demo_3.png", "London"),
        ("test/demo_11.png", "2DS43")
    ]

    with open(output_file, 'w') as f:
        for image_path, label in data:
            f.write(f"{image_path}\t{label}\n")

def fix_lines(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # If the line doesn't have a tab, add one after the first space
            if '\t' not in line:
                # Find the first space in the line
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    parts[1] = parts[1].strip()
                    # Add a tab between the image name and the label
                    fixed_line = f"{parts[0]}\t{parts[1]}"
                else:
                    # If there is no space, write the line as is
                    fixed_line = line.strip()
            else:
                # If the line already has a tab, write it as is
                fixed_line = line.strip()

            # Write the fixed line to the output file
            outfile.write(fixed_line + '\n')

if __name__ == "__main__":
    # generate_gt_file("gt.txt")
    fix_lines("data\gt.txt", "data\gt_new.txt")
