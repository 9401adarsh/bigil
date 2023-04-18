import hashlib


testString = str('70f073d3fb50f810')
print(len(testString))
##hexString = '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005'
hexString = '0'*112 + testString
print(f'len(hexString) = {len(hexString)}. # bits = {len(hexString) * 4}')
preimage = bytes.fromhex(hexString)


print(preimage)
print((int(preimage.hex(), 16)))  # binary representation of pre-image
# output is '0b101'
preimageLen = len(preimage)
print(preimageLen)  # length of pre-image
result = hashlib.sha256(preimage).hexdigest()  # compute hash
# output is
# 'c6481e22c5ff4164af680b8cfaa5e8ed3120eeff89c4f307c4a6faaae059ce10'
print(result)
print(len(result))
print(type(result))

unpackedResult = [result[:32], result[32:]]
print(unpackedResult)
unpackedResult = [int(i, 16) for i in unpackedResult]
print(unpackedResult)
