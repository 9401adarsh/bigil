import os
import subprocess
from typing import *
import json


class arbitrationZok:
    def __init__(self, zokFilename, cwd=None) -> None:
        self.cwd = cwd if cwd is not None else os.getcwd()
        self.zokFilePath = cwd + '/' + zokFilename
        subprocess.run(["zokrates", "compile", "-i", self.zokFilePath])
        subprocess.run(["zokrates", "setup"])
        pass

    def setup(self):
        subprocess.run(["zokrates", "setup"], cwd=self.cwd)
        return

    def genWitness(self, preImage, hashDigest: str):
        # give input as a list and and each argument as a string
        preImageInput = ['0', '0', '0', str(int(preImage, base=16))]
        hashDigestInput = [hashDigest[:32], hashDigest[32:]]
        unpackedHashDigest = [str(int(i, 16)) for i in hashDigestInput]
        inputList = preImageInput + unpackedHashDigest
        commandToRun = ["zokrates", "compute-witness", "-a"] + inputList
        ##print(commandToRun)
        result = subprocess.run(commandToRun, capture_output=True)
        return result.stdout.decode('utf-8')

    def genProof(self):
        subprocess.run(["zokrates", "generate-proof"])
        pass

    def verifyProof(self) -> bool:
        result = subprocess.run(["zokrates", "verify"], capture_output=True)
        print(result)
        if result.stdout.decode('utf-8') == 'Performing verification...\nPASSED\n':
            ##print('Verification is a success')
            return True
        ##print('Verification is a bust.')
        return False

    def flushFiles(self, genWitness: bool):
        pass

    def simulator(self, preImage, hashDigest):
        output = self.genWitness(preImage, hashDigest)
        if output != 'Computing witness...\nWitness file written to \'witness\'\n':
            print('witnessGen failed')
            subprocess.run(["bash", os.getcwd() + "/flush.sh"])
            return False, None
        self.genProof()
        proofPath = 'proof.json'
        ##print(os.getcwd())
        ##print(proofPath)
        proofJSON = json.load(open(proofPath, 'r'))
        ##print(proofJSON)
        answer = self.verifyProof()
        subprocess.run(["bash", "./flush.sh"])
        subprocess.run(["bash", "./flush-1.sh"])
        return answer, proofJSON