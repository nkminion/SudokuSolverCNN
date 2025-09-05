from PIL import ImageFont,ImageDraw,Image
import numpy as np
import os

#Make Custom Dataset

FontPath = 'PyTorch/Fonts'
ImgPath = 'PyTorch/CustomDataset'

for Font in os.listdir(FontPath):
	if Font.endswith('ttf'):
		try:
			font = ImageFont.truetype(os.path.join(FontPath,Font),24)
			for i in range(10):
				ImgDir = os.path.join(ImgPath,str(i))
				os.makedirs(ImgDir,exist_ok=True)
				img = Image.new('L',(28,28),color=0)
				draw = ImageDraw.Draw(img)
				draw.text((14,14),str(i),font=font,fill=255,anchor='mm')
				img.save(os.path.join(ImgDir,f"{Font}.png"))
		except (OSError,IOError):
			print(f"Could not load font {Font}!")

print(f"Images have been saved to {ImgPath}")