from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dashscope import ImageSynthesis

background_image = Image.open("/app/resources/background.png")

def resize_and_crop(img, target_width=154, target_height=240):
    if isinstance(img, bytes):
        img = Image.open(BytesIO(img))
    original_width, original_height = img.size

    scale_ratio = target_height / original_height

    new_width = int(original_width * scale_ratio)
    new_height = target_height

    img = img.resize((new_width, new_height), Image.LANCZOS)

    left = max((new_width - target_width) / 2, 0)
    top = 0
    right = left + target_width
    bottom = new_height

    img = img.crop((left, top, right, bottom))
    return img

def image_to_base64(image: Image.Image, fmt='png') -> str:
    image = resize_and_crop(image)
    output_buffer = BytesIO()
    image.save(output_buffer, format=fmt)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return f'data:image/{fmt};base64,' + base64_str

def fill_image(name, prompt):
    img = background_image.copy()
    width, height = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/app/resources/font.ttf", 72)
    text = f"{name}\n{prompt}"
    text_bbox = font.getbbox(text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((width - text_width) / 2, (height - text_height) / 2)
    draw.text(position, text, font=font, fill="black")
    return image_to_base64(img)

async def gen_image(input_prompt):
    for _ in range(3):
        response = ImageSynthesis.call(
            model="flux-schnell", 
            prompt=input_prompt, 
            size='1024*1024'
        )
        if response.status_code == HTTPStatus.OK and response.output.task_status == "SUCCEEDED":
            image_url = response.output.results[-1].url
            image = requests.get(image_url)
            return image_to_base64(image.content)
    return None


    