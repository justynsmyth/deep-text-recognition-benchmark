from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms
import os
import string
from datetime import datetime, timedelta
import random
import numpy as np

random.seed(1029)

FONTS_DIR = './fonts'
TRAIN_DIR = './train-font-dataset-stacktype1'
VALID_DIR = './valid-font-dataset-stacktype1'
GT_FILE_TRAIN = os.path.join(TRAIN_DIR, 'gt-generated_stacktype1.txt')
GT_FILE_VALID = os.path.join(VALID_DIR, 'gt-generated_stacktype1.txt')

IMAGE_SIZE = (320, 128)  # (width, height)
BG_COLOR = (255, 255, 255)  # white background
BG_BROWN = (170, 150, 80) # brown background
TEXT_COLOR = (0, 0, 0)  # black text
TRAIN_SPLIT = 0.8  # Percentage of images to use as training data

def get_all_fonts(fonts_dir):
    """Returns a list of all font paths in the fonts directory."""
    return [os.path.join(fonts_dir, font) for font in os.listdir(fonts_dir) if font.endswith(('.ttf', '.otf'))]


def generate_dates(start_date, end_date):
    """Generates a list of dates from start_date to end_date in 'MM-DD' format."""
    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime('%#m-%#d')
        current_date += timedelta(days=1)

def generate_pieces():
    '''Generates a list of piece counts from 20 - 3000 pc format'''
    numbers = range(20, 3000)
    pc = 'PC'
    for number in numbers:
        yield f'{number}{pc}'

def generate_stacktype():
    '''Generates a list of stacktype identifers in the format 'CompanyTypeType'''
    companies = ['BNSF', 'BN', 'KI']
    labels = ['3', '4', '5', 'SG', 'IG', '10']
    wood = ['OAK', 'M', 'MIXED', 'MIX']
    for company in companies:
        for label in labels:
            # SG and IG: Skip 'OAK' and 'MIXED'
            if label in ['SG', 'IG']:
                # Yield both with and without wood_type, but exclude OAK and MIXED
                yield f'{company}{label}'  # No wood_type
            else:
                # For other labels: yield with and without wood_type
                yield f'{company}{label}'  # No wood_type
                for wood_type in wood:
                    yield f'{company}{label}{wood_type}'



def generate_identifiers():
    """Generates a list of identifiers in the format 'RoadSectionSideRow'."""
    roads = list(range(1, 12)) + ['FH']  # Roads from 1 to 11
    sections = string.ascii_uppercase[:5]  # Sections from 'A' to 'E'
    sides = ['N', 'E', 'W', 'S']  # Sides: North, East, West, South
    rows = list(range(1, 100)) + [f'{row}.5' for row in range(1, 100)]  # Rows from 1 to 99 including half stacks (.5)

    for road in roads:
        for section in sections:
            for side in sides:
                for row in rows:
                    yield f'{road}{section}{side}{row}'


def create_image_with_text(text, font_path, output_dir, gt_file, font_size=38,
                           augment=False, max_augmentations=3):
    """Creates an image with the specified text and font, optionally with augmentations."""
    img = Image.new('RGB', IMAGE_SIZE, BG_COLOR)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_path, font_size)

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((IMAGE_SIZE[0] - text_width) // 2, (IMAGE_SIZE[1] - text_height) // 2)

    draw.text(text_position, text, fill=TEXT_COLOR, font=font)

    if augment:
        img = apply_augmentations(img, max_augmentations)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_filename = f"{text}_{os.path.basename(font_path)}.png"
    image_path = os.path.join(output_dir, image_filename)
    img.save(image_path)

    generate_gtfile(gt_file, text, image_filename)
    return image_path

def generate_gtfile(output_file, date, img_filename):
    """Updates the ground truth file with the image filename and corresponding text."""
    with open(output_file, 'a') as f:
        f.write(f"{img_filename}\t{date}\n")

def apply_augmentations(img, max_augmentations):
    """Apply random augmentations to the image."""
    aug_transforms = transforms.Compose([
        transforms.RandomRotation(degrees=2),
        transforms.ColorJitter(brightness=0.1, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.98, 1.02), shear=2),
    ])
    for _ in range(random.randint(1, max_augmentations)):
        img = aug_transforms(img)

    img = add_random_noise(img)

    return img


def add_random_noise(img, scale=25):
    """Add random Gaussian noise to an image."""
    np_img = np.array(img).astype(np.float32)  # Ensure the image is in float to handle noise addition properly

    # Generate Gaussian noise with the specified scale (standard deviation)
    noise = np.random.normal(loc=0, scale=scale, size=np_img.shape)

    # Add the noise to the image and clip values to keep them within valid pixel range (0 to 255)
    new_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(new_img)

def main():
    if not os.path.exists(TRAIN_DIR):
        os.makedirs(TRAIN_DIR)
    if not os.path.exists(VALID_DIR):
        os.makedirs(VALID_DIR)

    if os.path.exists(GT_FILE_TRAIN):
        os.remove(GT_FILE_TRAIN)
    if os.path.exists(GT_FILE_VALID):
        os.remove(GT_FILE_VALID)

    # Generate all dates from 01-01 to 12-31
    # start_date = datetime(year=2024, month=1, day=1)
    # end_date = datetime(year=2024, month=12, day=31)

    # Get all fonts from the fonts directory
    fonts = get_all_fonts(FONTS_DIR)

    for identifier in generate_stacktype():
        for font_path in fonts:
            # Decide randomly whether this sample is for training or validation
            is_train = random.random() < TRAIN_SPLIT
            output_dir = TRAIN_DIR if is_train else VALID_DIR
            gt_file = GT_FILE_TRAIN if is_train else GT_FILE_VALID

            # Create original and augmented images
            create_image_with_text(identifier, font_path, output_dir, gt_file, augment=True)

if __name__ == "__main__":
    main()