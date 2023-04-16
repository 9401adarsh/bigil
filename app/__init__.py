import io
import os
import csv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from exif import Image as ei
from flask import Flask, render_template, request, make_response
from PIL import Image
from ETHBC import upload_commitment
from PC import Commitment, Message, PCParameters, PCVerifier

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
    params = PCParameters(int(dictionary['q']), int(
        dictionary['g']), int(dictionary['h']))
    v = PCVerifier(params)
    v.add(c)
    v.add(m)
    if v.verify():
        return True
    else:
        return False


def verify_signature(img_name, img_for_exif1):
    try:
        print("ya")
    except IOError:
        pass
    pb = ''
    key_name = img_name.split('.')[0] + '-key.pem'
    with open('./public_keys/' + key_name, "rb") as key_file:
        pb = serialization.load_pem_public_key(key_file.read())

    if img_for_exif1.list_all().count('copyright') > 0:
        cp_list = img_for_exif1.copyright.split('$')
        cr = cp_list[0].strip()
        ds = cp_list[1]
        print(cr, ds)
        if pb.verify(
                bytes.fromhex(ds),
                cr.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()) is None:
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
        img_name = image_file.filename
        image_bytes = image_file.read()
        img = Image.open(io.BytesIO(image_bytes))
        if img.getexif() == {}:
            return "Image has no EXIF data"
        img_for_exif = ei(io.BytesIO(image_bytes))
        x = verify_signature(img_name, img_for_exif)
        if x:
            if hash_comparison() < 0.5:
                if len(lines) > 0:
                    cm_dict = read_file(lines)
                    if verify_commitment(cm_dict) is True:
                        senderAddr = request.cookies.get('userWallet')
                        owner_addr = ''
                        with open('owner_info.csv', mode='r') as csv_file:
                            csv_reader = csv.reader(csv_file)
                            line_number = 0
                            for row in csv_reader:
                                line_number += 1
                                # compare the first value in each row with the search value
                                if row[0] == 'i4.jpg':
                                    # if a match is found, assign the second value to the variable
                                    owner_addr = row[1]
                                    break  # stop searching after the first match
                            else:
                                print("No match found.")
                        log = ''
                        for line in lines:
                            log = line + '$' + log
                        upload_commitment(
                            senderAddr, log, owner_addr, img_name)
                        return "modded image, storing edits to blockchain"
                    else:
                        return "invalid image"
                else:
                    return "similar images"
            else:
                csv_file_path = "owner_info.csv"

                # Check if file exists
                file_exists = os.path.isfile(csv_file_path)

                # If file does not exist, create a new CSV file with headers
                if not file_exists:
                    with open(csv_file_path, mode='w', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        # add your own headers here
                        writer.writerow(['filename', 'owner_addr'])

                owner_addr = request.cookies.get('userWallet')
                # Append a new line to the existing CSV file
                with open(csv_file_path, mode='a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([img_name, owner_addr])

                # store the image in dataStorage folder
                img.save('./dataStorage/' + img_name, exif=img.info['exif'])
                return "unique image"
        else:
            return "Signature is invalid"

        return 'EXIF data printed to console!'
    else:
        return render_template('index.html')


@app.route('/api/wallet', methods=['GET', 'POST'])
def wallet():
    if request.method == 'POST':
        wallet_address = request.get_json()['walletAddress']
        # print(request.get_json()['walletAddress'])
        response = make_response()  # We can also render new page with render_template
        response.set_cookie('userWallet', wallet_address)
        return response
    else:
        response = make_response()
        response.delete_cookie('userWallet')
        return response


if __name__ == '__main__':
    app.run()
