from PIL import Image, ImageDraw, ImageFont
import numpy as np

items = ['1) 24-08-2022, Доход, Не определён, 300.0, Brush’s\n',
         '2) 24-08-2022, Доход, Не определён, 200.0, Машина\n',
         '3) 17-08-2022, Доход, Не определён, 555.0, asdsf']

img = Image.new(mode="RGB", size=(max([len(i) for i in items]) * 25 // 2 + 10, (22 * len(items) * 2) + 20), color=(255, 255, 255))
font = ImageFont.truetype("arial.ttf", 25)
drawer = ImageDraw.Draw(img)
drawer.text((10, 10),
            ''.join(items),
            font=font,
            fill='black',
            spacing=30)
img.show()