import re

import easyocr
from PIL import Image

reader = easyocr.Reader(['en'], gpu=True)


def scan_attributes(text, image):
    results = reader.readtext(image)

    found_text = [result for result in results if text in result[1]]

    if found_text:
        for result in found_text:
            bounding_box = result[0]

            if len(bounding_box) == 4:
                # x_min = min(bounding_box[0][0], bounding_box[3][0])
                y_min = min(bounding_box[0][1], bounding_box[1][1])
                x_max = max(bounding_box[1][0], bounding_box[2][0])
                y_max = max(bounding_box[2][1], bounding_box[3][1])

                if text == 'MAX COMBO':
                    y_min *= 0.95
                    y_max *= 1.05

                right_width = 400
                right_coordinates = (x_max, y_min, x_max + right_width, y_max)

                image = Image.open(image)
                attrib_image = image.crop(right_coordinates)
                attrib_image.save(f'{text}.png')

                scanned_attrib = reader.readtext(f'{text}.png', detail=0, allowlist="0123456789", mag_ratio=4, text_threshold=0.1)

                print(scanned_attrib)
                return int(re.compile("(\d+)").match(scanned_attrib[0]).group(1))

            else:
                print("Invalid bounding box format")

    else:
        print(results)
        print(f"'{text}' not found in the OCR results.")


def scan_title(image):
    results = reader.readtext(image, paragraph=True)
    return results


def get_score_attributes(image):
    attribs = []
    title = scan_title(image)
    attribs.append(title[1][1])
    attribs.append(title[0][1])
    attribs.append(scan_attributes('PERFECT', image))
    attribs.append(scan_attributes('GREAT', image))
    attribs.append(scan_attributes('GOOD', image))
    attribs.append(scan_attributes('BAD', image))
    missscan = scan_attributes('MISS', image)
    if missscan is None:
        missscan = scan_attributes('MSS', image)
    attribs.append(missscan)
    attribs.append(scan_attributes('MAX COMBO', image))

    return attribs
