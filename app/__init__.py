from flask import Flask, request, render_template
from exif import Image as ei
from PIL import Image
import io
from PIL import Image
from PIL.ExifTags import TAGS
from exif import Image as ei
image_file = "i4.jpg"
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from PC import PCVerifier, Commitment, Message, PCParameters

app = Flask(__name__)

def hash_comparison():
    return 0.4

def read_file(lines):
    # Iterate over the lines
    dictionary = {}
    for line in lines:
        print(line)
        # Split the line into key-value pairs
        key, value = line.split(' | ')
        
        # Add the key and sub-values to the dictionary
        dictionary[key] = value

    # Print the dictionary
    return dictionary

def verify_commitment(dictionary):
    c = Commitment(int(dictionary['c']))
    m = Message(dictionary['M'], int(dictionary['r']))
    params = PCParameters(int(dictionary['q']), int(dictionary['g']), int(dictionary['h']))
    v = PCVerifier(params)
    v.add(c)
    v.add(m)
    if v.verify():
        return True
    else:
        return False


def verify_signature(image1, img_for_exif1):
    try:
        print("ya")
    except IOError:
        pass
    pb = ''
    with open("key.pem", "rb") as key_file:
        pb = serialization.load_pem_public_key(key_file.read())
    if img_for_exif1.list_all().count('Copyright') > 0:
        cr = img_for_exif1.copyright.split('$')[0].strip()
        ds = img_for_exif1.copyright.split('$')[1]
        if pb.verify(bytes.fromhex(ds),cr.encode(),padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256()) is None:
            print("Signature is valid")
            return True
        else:
            print("Signature is invalid")
            return False
    else:
        return False


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        image_file = request.files['image_file']
        text_file = request.files['text_file']
        lines = text_file.read().decode('utf-8').splitlines() if text_file else []
        image_bytes = image_file.read()
        img = Image.open(io.BytesIO(image_bytes))
        if img.getexif() is None:
            return "Image has no EXIF data"
        else:
            print(img.getexif())
        img_for_exif = ei(io.BytesIO(image_bytes))
        print(img_for_exif.list_all())
        x = verify_signature(img, img_for_exif)
        if x:
            if hash_comparison() < 0.5:
                if len(lines) > 0:
                    cm_dict = read_file(lines)
                    if verify_commitment(cm_dict) is True:
                        return "modded image, storing edits to blockchain"
                    else:
                        return "invalid image"
                else:
                    return "similar images"
            else:
                return "different images"
        else:
            return "Signature is invalid"

        return 'EXIF data printed to console!'
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()
