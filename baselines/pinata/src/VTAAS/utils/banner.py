from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def add_banner(image_bytes: bytes, text: str, banner_height: int = 50):
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size

    new_height = height + banner_height
    new_image = Image.new("RGB", (width, new_height), (255, 255, 255))

    new_image.paste(image, (0, banner_height))

    draw = ImageDraw.Draw(new_image)
    draw.rectangle([0, 0, width, banner_height], fill=(200, 0, 0))

    # try:
    #     font = ImageFont.truetype("arial.ttf", 20)
    # except IOError:
    font = ImageFont.load_default(size=18)

    text_bbox = draw.textbbox((0, 0), text=text, font=font)
    text_width = int(text_bbox[2] - text_bbox[0])
    text_height = int(text_bbox[3] - text_bbox[1])
    text_x: int = (width - text_width) // 2
    text_y: int = (banner_height - text_height) // 2

    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    img_byte_arr = BytesIO()
    new_image.save(img_byte_arr, format="PNG")

    return img_byte_arr.getvalue()


# Quick testing
# with open(
#     "./../../../screenshots/f70de474aea14f34a0788d0d6f06203e_act_2025-02-03_12-12-56.png",
#     "rb",
# ) as f:
#     image_bytes = f.read()
#
# modified_bytes = add_banner(image_bytes, "Screenshot Analysis")
#
# with open("./../../../screenshots/output_image.png", "wb") as f:
#     f.write(modified_bytes)
#
# print("Modified image saved.")
