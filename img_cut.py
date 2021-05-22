from PIL import Image

img = Image.open(r"C:\Users\Administrator\Desktop\g.jpg")
print(img.size)
cropped = img.crop((500, 0, 3400, 2736))  # (left, upper, right, lower)
cropped.save(r"C:\Users\Administrator\Desktop\g_cut1.jpg")
