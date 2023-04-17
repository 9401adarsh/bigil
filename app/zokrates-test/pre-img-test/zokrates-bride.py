import os
import subprocess


class zokratesBridge:
    def __init__(self, zokFilename, cwd=None) -> None:
        self.cwd = cwd if cwd is not None else os.getcwd()
        self.zokFilePath = cwd + '/' + zokFilename
        subprocess.run(["zokrates", "compile", "-i", self.zokFilePath])
        subprocess.run(["zokrates", "setup"], cwd=self.cwd)
        pass

    def setup(self):
        subprocess.run(["zokrates", "setup"], cwd=self.cwd)
        return

    def genWitness(self, input):
        # give input as a list and and each argument as a string
        print(input)
        commandToRun = ["zokrates", "compute-witness", "-a"] + input
        print(commandToRun)
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

    def simulator(self, witnessInput):
        output = self.genWitness(witnessInput)
        if output != 'Computing witness...\nWitness file written to \'witness\'\n':
            return False
        self.genProof()
        answer = self.verifyProof()
        subprocess.run(["rm", "witness"])
        subprocess.run(["rm", "proof.json"])
        return answer


cwd = os.getcwd()
zokFilename = 'hash.zok'

zokBridge = zokratesBridge(zokFilename, cwd)
if zokBridge.simulator(witnessInput=['0', '0', '0', '5']):
    print('Verification is a success')
else:
    print('Verification is a bust.')
