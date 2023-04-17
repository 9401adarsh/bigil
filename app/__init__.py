from spihtWorkflow.spihtHashCompare import compareAgainstImagesInCloud
from PC import Commitment, Message, PCParameters, PCVerifier
from ETHBC import unique_img_transact, upload_commitment
from PIL import Image
from flask import Flask, make_response, render_template, request, send_file, send_from_directory
from exif import Image as ei
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import csv
import io
import base64
import os
import csv

spaceLog = 'metrics/spaceLog.csv'


app = Flask(__name__)


def hash_comparison(img):
    tuple_res = compareAgainstImagesInCloud(img)
    candidate_img = tuple_res[0]
    comparison_metric = tuple_res[1]
    sign1 = img.getexif()[33432]
    sign2 = candidate_img.getexif()[33432]
    equal_sig_flag = False
    if sign1 == sign2:
        equal_sig_flag = True
    return candidate_img, comparison_metric, equal_sig_flag


def store_owner_info(owner_addr, img_id):
    csv_file_path = "owner_info.csv"
    # Check if file exists
    file_exists = os.path.isfile(csv_file_path)
    # If file does not exist, create a new CSV file with headers
    if not file_exists:
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            # add your own headers here
            writer.writerow(['filename', 'owner_addr'])
    # Append a new line to the existing CSV file
    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([img_id, owner_addr])


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
    user_id = img_for_exif1.copyright.split('$')[0].strip()
    key_name = user_id + '-key.pem'  # hardcoded, to change
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
    flag = 0
    if request.method == 'POST':
        image_file = request.files['image_file']
        text_file = request.files['text_file']
        lines = text_file.read().decode('utf-8').splitlines() if text_file else []
        img_name = image_file.filename
        image_bytes = image_file.read()

        img = Image.open(io.BytesIO(image_bytes))
        if img.getexif() == {}:
            return "Image has no EXIF data, Invalid Image"

        img_for_exif = ei(io.BytesIO(image_bytes))
        x = verify_signature(img_name, img_for_exif)

        if x:
            candidate_img, comparison_metric, equal_sig_flag = hash_comparison(
                img)
            ans = os.path.split(candidate_img.filename)
            # if comparison_metric == 0:
            #     if(equal_sig_flag):
            #         return "equal images, cant upload, bye bye - here is the link of image you wanted"
            #     else:
            #         return "equal images, but different signatures, so cant upload cos you ripped someone off"
            if comparison_metric <= 25:
                if len(lines) > 0:
                    cm_dict = read_file(lines)
                    verify_flag = verify_commitment(cm_dict)
                    if verify_flag is True:
                        if equal_sig_flag:
                            senderAddr = request.cookies.get('userWallet')
                            owner_addr = ''
                            with open('owner_info.csv', mode='r') as csv_file:
                                csv_reader = csv.reader(csv_file)
                                for row in csv_reader:
                                    if row[0] == ans[1]:
                                        owner_addr = row[1]
                                        break
                                else:
                                    print("No match found.")
                            log = ''
                            for line in lines:
                                log = line + '$' + log
                            log = '###' + log + '###'
                            # print(ans)
                            tf_path = './transform_logs/' + \
                                senderAddr + '_' + ans[1] + '_log.txt'
                            with open(tf_path, 'w') as f:
                                f.write(log)
                            #print(senderAddr, log, owner_addr, ans[1])
                            #print(img.format, candidate_img.format)
                            o_img = img
                            name1 = "tempstore/t1." + str(img.format).lower()
                            o_img = o_img.save(name1)
                            c_img = candidate_img
                            name2 = "tempstore/t2." + \
                                str(candidate_img.format).lower()
                            c_img = c_img.save(name2)

                            row_data = [1, (os.stat(name1).st_size+os.stat(
                                name2).st_size), (os.stat(
                                    name2).st_size + os.stat(tf_path).st_size)]
                            with open(spaceLog, 'a', newline='') as f_new:
                                writer = csv.writer(f_new)
                                writer.writerow(row_data)
                                f_new.close()
                            # delete temp images
                            os.remove(name1)
                            os.remove(name2)
                            upload_commitment(
                                senderAddr, log, owner_addr, ans[1])
                            return "modded image, storing edits to blockchain"
                        else:
                            return "Invalid Image"
                    else:
                        return "invalid image"
                else:
                    if equal_sig_flag:
                        data = io.BytesIO()
                        candidate_img.save(data, candidate_img.format)
                        encoded_img_data = base64.b64encode(data.getvalue())
                        return render_template('index.html', img_data=encoded_img_data.decode('utf-8'), img_name=ans[1])
                        # return "Same image uploaded before, cant be uploaded again, here is link of orig img"
                    else:
                        return "Invalid Image, you can try appealing"
            else:
                owner_addr = request.cookies.get('userWallet')
                store_owner_info(owner_addr, img_name)
                # store the image in dataStorage folder
                img.save('./dataStorage/' + img_name, exif=img.info['exif'])
                # call the smart contract function
                unique_img_transact(owner_addr, img_name)
                return "unique image"
        else:
            return "Signature is invalid"
    else:
        return render_template('index.html')


@app.route('/api/wallet', methods=['GET', 'POST'])
def wallet():
    if request.method == 'POST':
        wallet_address = request.get_json()['walletAddress']
        response = make_response()
        response.set_cookie('userWallet', wallet_address)
        return response
    else:
        response = make_response()
        response.delete_cookie('userWallet')
        return response


@app.route('/download', methods=['POST'])
def download_image():
    filename = request.form['img_name']
    directory = './dataStorage'
    return send_file(os.path.join(directory, filename))


@app.route('/arbitration', methods=['GET', 'POST'])
def arbitration():
    return render_template('arbitration.html')


if __name__ == '__main__':
    app.run()
