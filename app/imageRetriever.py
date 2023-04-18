import os
from PIL import Image
from PIL import ImageFilter


def imageRetriever(img, text_path=None):
    imageObject = img

    if(text_path == None):
        return imageObject
    else:
        id = ""
        with open(text_path, "r") as fi:
            for ln in fi:
                if ln.startswith("M |"):
                    id = (ln[4:].strip())

        print(id)
        tf_list = id.split(";")

        for tf in tf_list:
            tf = tf.rstrip().lstrip()
            cmd = tf.split(" ")
            temp_path = "tempstore/temp.jpg"

            if cmd[0] == "GB":
                imageObject = imageObject.filter(
                    ImageFilter.GaussianBlur(radius=int(cmd[1])))
                # imageObject.show()
            elif cmd[0] == "B":
                imageObject = imageObject.convert('1')
                # imageObject.show()
            elif cmd[0] == "S":
                imageObject = imageObject.filter(ImageFilter.SHARPEN)
                # imageObject.show()
            elif cmd[0] == "EE":
                imageObject = imageObject.filter(ImageFilter.EDGE_ENHANCE)
                # imageObject.show()
            elif cmd[0] == "C":
                t_img = imageObject.save(
                    temp_path, optimize=True, quality=int(cmd[1]))
                imageObject = Image.open(temp_path)
                # imageObject.show()
            else:
                continue

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return imageObject


# img = Image.open("test_imgs/lena.jpg")
# i = imageRetriever(img, "transformLogExample.txt")
# i.show()
