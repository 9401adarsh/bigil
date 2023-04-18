import base64
import csv
import io
import os
import hashlib
import json

from exif import Image as ei
from flask import (Flask, make_response, render_template, request, send_file)
from PIL import Image

from ETHBC import unique_img_transact, upload_commitment
from ETHBC2 import *
from dedupUtils import *
from spihtWorkflow.spihtHashCompare import *

from arbitration import *

from zokratesTest.arbSnarkTest.arbSnark import arbitrationZok

comparison_threshold = 25

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        image_file, text_file = request.files['image_file'], request.files['text_file']
        lines = text_file.read().decode('utf-8').splitlines() if text_file else []
        img_name = image_file.filename
        image_bytes = image_file.read()
        img = Image.open(io.BytesIO(image_bytes))
        if img.getexif() == {}:
            return "Image has no EXIF data, Invalid Image"
        img_for_exif = ei(io.BytesIO(image_bytes))
        sig_validity = verify_signature(img_name, img_for_exif)
        print(img_for_exif.list_all())
        if sig_validity:
            candidate_img, comparison_metric, equal_sig_flag = hash_comparison(
                img)
            candidate_img_fname = os.path.split(candidate_img.filename)[1] if candidate_img else None
            # if comparison_metric == 0:
            #     if(equal_sig_flag):
            #         return "equal images, cant upload, bye bye - here is the link of image you wanted"
            #     else:
            #         return "equal images, but different signatures, so cant upload cos you ripped someone off"
            if comparison_metric <= comparison_threshold:
                if len(lines) > 0:
                    cm_dict = read_file(lines)
                    transform_log, verify_flag = verify_commitment(cm_dict)
                    if verify_flag is True:
                        if equal_sig_flag:
                            senderAddr = request.cookies.get('userWallet')
                            log, owner_addr, tf_path = store_info(
                                senderAddr, candidate_img_fname, lines, transform_log)
                            #print(senderAddr, log, owner_addr, candidate_img_fname)
                            #print(img.format, candidate_img.format)
                            store_temp(img, candidate_img, tf_path)
                            upload_commitment(
                                senderAddr, log, owner_addr, candidate_img_fname)
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
                        return render_template('index.html', img_data=encoded_img_data.decode('utf-8'), img_name=candidate_img_fname)
                        # return "Same image uploaded before, cant be uploaded again, here is link of orig img"
                    else:
                        return "Invalid Image, you can try appealing"
            else:
                owner_addr = request.cookies.get('userWallet')
                print(owner_addr, img_name)
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


@app.route('/retrieval', methods=['GET', 'POST'])
def retrieval():
    if request.method == 'POST':
        pass
    else:
        userAddr = request.cookies.get('userWallet')
        if userAddr:
            list_of_i = search_images(userAddr)
            imagelist = []
            for i in list_of_i:
                data = io.BytesIO()
                i.save(data, 'JPEG')
                encoded_img_data = base64.b64encode(data.getvalue())
                imagelist.append(str(encoded_img_data))
            return render_template('retrieval.html', imagelist=imagelist)
        else:
            return 'Please login first'


@app.route('/download', methods=['POST'])
def download_image():
    filename = request.form['img_name']
    directory = './dataStorage'
    return send_file(os.path.join(directory, filename))


@app.route('/arbitration', methods=['GET', 'POST'])
def arbitration():
    if request.method == 'POST':
        image_file = request.files['image_file']
        image_bytes = image_file.read()
        img = Image.open(io.BytesIO(image_bytes))
        userAddr = request.cookies.get('userWallet')
        call_stake(userAddr, 0.1)
        candidate_img, comparison_metric, equal_sig_flag = hash_comparison(img)
        flag = compare_images(img, candidate_img)
        if flag:
            arbitration_fail(userAddr)
            zokratesDirectory = os.getcwd() + '/zokratesTest/arbSnarkTest'
            zokObject = arbitrationZok('arb-snark.zok', zokratesDirectory)
            wHash = computeWHash(candidate_img)
            wHashStr = '0'*112 + wHash.__str__()
            preimage = bytes.fromhex(wHashStr)
            hashDigest = hashlib.sha256(preimage).hexdigest()
            verificationResult = zokObject.simulator(wHash.__str__(), hashDigest)
            return "Images are too similar, arbitration failed\n\n" +  json.dumps(verificationResult[1])
        else:
            arbitration_success(userAddr)
            return "Images are not similar, arbitration successful, apologies for the inconvenience"
    else:
        return render_template('arbitration.html')


if __name__ == '__main__':
    app.run()
