import easyocr

def main():
    reader = easyocr.Reader(['en'], recog_network='best_accuracy')
    image_path = 'demo_1.png'
    result = reader.readtext(image_path)
    # Print the detected text
    for detection in result:
        print(detection[1])  # The detected text

if __name__ == "__main__":
    main()