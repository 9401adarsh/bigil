import csv
import os
from mailbox import Message

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from PC import Commitment, PCParameters, PCVerifier
from spihtWorkflow.spihtHashCompare import compareAgainstImagesInCloud


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
