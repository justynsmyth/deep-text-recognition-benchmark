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


if __name__ == "__main__":
    generate_gt_file("gt.txt")
