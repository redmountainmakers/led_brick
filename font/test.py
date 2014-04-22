from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from numpy import array

image = Image.new('RGB', (29, 6))
draw = ImageDraw.Draw(image)
font = ImageFont.load('6by6tall.pil')
text = "Hello!"

center = tuple((array(image.size) - array(draw.textsize(text, font=font))) / 2)

draw.text(center, text, font=font, fill=(255,255,255))
image.save('test.png')
