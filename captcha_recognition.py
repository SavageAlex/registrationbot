from PIL import Image
from operator import itemgetter

im = Image.open("./captcha_images/captcha.png")
with im:
    im = im.convert("P")

    his = im.histogram()

    values = {i : his[i] for i in range(256)}

    print(values)

    for k, v in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
        print(k, v)

    print(im.size)

    im2 = Image.new("p", im.size, 255)

    temp = {}

    for x in range(im.size[1]):
        for y in range(im.size[0]):
            pix = im.getpixel((y,x))
            temp[pix] = pix
            if pix == 2:
                im2.putpixel((y, x), 0)
    im2.save("output.gif")