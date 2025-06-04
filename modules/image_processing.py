from PIL import Image, ImageDraw, ImageFont, ImageOps, ExifTags
import base64
from io import BytesIO
import os
import shutil
import logging

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image.getexif()
        if exif is not None:
            orientation = exif.get(orientation, 1)

            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return image

def add_watermark(image_data, einsatzstichwort, einsatzmeldung, einsatzbericht, img_x, img_y, img_width, img_height, font_Einsatzstichwort_path, font_Headline_path, static_folder, upload_folder, imagealarmbanner, imagewatermark, symbolicimagetag):
    logging.info('add_watermark')

    if isinstance(image_data, str) and image_data.startswith('data:image'):
        image_data = image_data.split(",")[1]
        image_data = base64.b64decode(image_data)
    else:
        image_data = base64.b64decode(image_data)

    image = Image.open(BytesIO(image_data)).convert('RGBA')
    image = correct_image_orientation(image)
    image = image.resize((img_width, img_height), Image.LANCZOS)
    new_base = Image.new('RGBA', (1080, 1080), (255, 255, 255, 0))
    new_base.paste(image, (img_x, img_y))
    image = new_base

    if imagealarmbanner:
        scale_factor = 16
        high_res_polygon_img = Image.new('RGBA', (image.width * scale_factor, image.height * scale_factor), (255, 255, 255, 0))
        
        d = ImageDraw.Draw(high_res_polygon_img)

        polygon1 = [(0, 600 * scale_factor), (400 * scale_factor, 575 * scale_factor), (400 * scale_factor, 625 * scale_factor), (0, 650 * scale_factor)]
        polygon2 = [(100 * scale_factor, 642 * scale_factor), (300 * scale_factor, 630 * scale_factor), (300 * scale_factor, 662 * scale_factor), (100 * scale_factor, 675 * scale_factor)]

        d.polygon(polygon1, fill=(255, 0, 0, 255))
        d.polygon(polygon2, fill=(200, 0, 0, 255))

        fnt = ImageFont.truetype(font_Einsatzstichwort_path, 16 * scale_factor)

        polygon_img = high_res_polygon_img.resize((image.width, image.height), Image.LANCZOS)

        text_img = Image.new('L', (500 * scale_factor, 50 * scale_factor))
        d = ImageDraw.Draw(text_img)
        if len(einsatzstichwort) <= 11:
            fnt = ImageFont.truetype(font_Headline_path, 32 * scale_factor)
        else:
            fnt = ImageFont.truetype(font_Headline_path, 26 * scale_factor)
        text_bbox = d.textbbox((0, 0), einsatzstichwort, font=fnt)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        d.text((0, 0), einsatzstichwort, font=fnt, fill=255)
        w = text_img.rotate(4, expand=1)

        w = w.resize((w.width // scale_factor, w.height // scale_factor), Image.LANCZOS)

        
        special_x = 197
        if "_" in einsatzstichwort:
            if len(einsatzstichwort) > 10:
                special_y = 618
            if len(einsatzstichwort) <= 10:
                special_y = 608
        else:
            if len(einsatzstichwort) > 10:
                special_y = 618
            if len(einsatzstichwort) <= 3:
              special_y = 608
            else:
                special_y = 610

        logging.debug(special_y)
       

        x = special_x - (text_w // (2 * scale_factor))
        y = special_y - (text_h // (2 * scale_factor))

        polygon_img.paste(ImageOps.colorize(w, (0, 0, 0), (255, 255, 255)), (x, y), w)


        fixed_text = "EINSATZALARM!"
        fixed_text_img = Image.new('L', (500 * scale_factor, 50 * scale_factor))
        d = ImageDraw.Draw(fixed_text_img)
        fnt2 = ImageFont.truetype(font_Headline_path, 45 * scale_factor)
        text_bbox = d.textbbox((0, 0), fixed_text, font=fnt2)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        d.text((0, 0), fixed_text, font=fnt2, fill=255)
        w = fixed_text_img.rotate(4, expand=1)

        w = w.resize((w.width // scale_factor, w.height // scale_factor), Image.LANCZOS)

        special_fixed_x = 200
        special_fixed_y = 573

        x = special_fixed_x - (text_w // (2 * scale_factor))
        y = special_fixed_y - (text_h // (2 * scale_factor))

        polygon_img.paste(ImageOps.colorize(w, (0, 0, 0), (255, 255, 255)), (x, y), w)

        watermarked = Image.alpha_composite(image, polygon_img)
    else:
        watermarked = image

    if imagewatermark:
        additional_image_path = os.path.join(static_folder, 'watermark.png')
        if os.path.exists(additional_image_path):
            additional_image = Image.open(additional_image_path).convert('RGBA')
            additional_image = additional_image.resize((447, 100), Image.LANCZOS)
            watermarked.paste(additional_image, (600, 950), additional_image)

    if symbolicimagetag:
            symbolicimagetext = "Symbolbild"
            symbolicimagetext_x = 30
            symbolicimagetext_y = 1030
            symbolicimagetext_shadow = (1, 1, 1, 1)

            d = ImageDraw.Draw(watermarked)
            fnt2 = ImageFont.truetype(font_Headline_path, 20)
            d.text((symbolicimagetext_x, symbolicimagetext_y), symbolicimagetext, font=fnt2, fill="lightgrey")


    output_path = os.path.join(upload_folder, 'einsatzbild.png')
    watermarked.save(output_path)
    
    static_output_path = os.path.join(static_folder, 'einsatzbild.png')
    shutil.copy(output_path, static_output_path)
    
    return static_output_path
