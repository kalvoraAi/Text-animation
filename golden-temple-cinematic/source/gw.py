import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
f=ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf',120,layout_engine=ImageFont.Layout.RAQM)
W,H=1080,300; txt='ਵਾਹਿਗੁਰੂ'
img=Image.new('RGBA',(W,H),(0,0,0,0))
sh=Image.new('RGBA',(W,H),(0,0,0,0))
ImageDraw.Draw(sh).text((W/2,H/2),txt,font=f,fill=(0,0,0,170),anchor='mm',language='pa')
sh=sh.filter(ImageFilter.GaussianBlur(6))
img.alpha_composite(sh)
ImageDraw.Draw(img).text((W/2,H/2),txt,font=f,fill=(232,199,122,255),anchor='mm',language='pa')
img.save(sys.argv[1])
