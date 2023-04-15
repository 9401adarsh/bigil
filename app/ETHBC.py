import json
from web3 import Web3

# Fill in your infura API key here
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

def upload_commitment(senderAddr, log, owner_addr, img_id):
            # Set a default account to sign transactions - this account is unlocked with Ganache
    # web3.eth.default_account = web3.eth.accounts[0]
    print('hello from upload_commitment')
    # sender_addr = web3.to_checksum_address(senderAddr) # FILL ME IN
    # address = web3.to_checksum_address('0x464ec18f27f6b12919aa8954ED3120302994A528') # FILL ME IN
    # # Initialize contract
    # contract = web3.eth.contract(address=address, abi=abi)

    # # Call the contract function
    # tx_hash = contract.functions.logTransformation(log, owner_addr, img_id).transact({'from': web3.eth.accounts[0], 'value': web3.toWei(0.1, 'ether')})
    # # # Set a new greeting

# OMG Address
abi = json.loads('''
[
	{
		"inputs": [
			{
				"internalType": "address payable",
				"name": "_serverAddress",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "imageId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "log",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "uploaderName",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "address",
				"name": "ownerAddress",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "amountSent",
				"type": "uint256"
			}
		],
		"name": "TransformationLogged",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "greet",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_log",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_uploaderName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "_ownerAddress",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_imageId",
				"type": "uint256"
			}
		],
		"name": "logTransformation",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "message",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "serverAddress",
		"outputs": [
			{
				"internalType": "address payable",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "transformations",
		"outputs": [
			{
				"internalType": "string",
				"name": "log",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "uploaderName",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "ownerAddress",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "imageId",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
''')

# Set a default account to sign transactions - this account is unlocked with Ganache
web3.eth.default_account = web3.eth.accounts[0]

address = web3.to_checksum_address('0x464ec18f27f6b12919aa8954ED3120302994A528') # FILL ME IN
# Initialize contract
contract = web3.eth.contract(address=address, abi=abi)
# Read the default greeting
print(contract.functions.greet().call())
# # Set a new greeting
# tx_hash = contract.functions.setGreeting('HEELLLLOOOOOO!!!').transact()
# # Wait for transaction to be mined
# web3.eth.waitForTransactionReceipt(tx_hash)
# # Display the new greeting value
# print('Updated contract greeting: {}'.format(
#     contract.functions.greet().call()
# ))