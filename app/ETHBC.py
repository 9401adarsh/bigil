import json
from web3 import Web3

# Fill in your infura API key here
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# OMG Address
abi = json.loads('''
[
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "string",
				"name": "imageId",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "log",
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
				"internalType": "address",
				"name": "_ownerAddress",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "_imageId",
				"type": "string"
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
				"internalType": "string",
				"name": "",
				"type": "string"
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
				"internalType": "address",
				"name": "ownerAddress",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "imageId",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
''')


def upload_commitment(senderAddr, log, owner_addr, img_id):
            # Set a default account to sign transactions - this account is unlocked with Ganache
    web3.eth.default_account = web3.eth.accounts[0]
    print('hello from upload_commitment')
    sender_addr = web3.to_checksum_address(senderAddr) # FILL ME IN
    address = web3.to_checksum_address('0x2ab39d682e080b50094e90A9794E34E3F6B4eb11') # FILL ME IN
    # # Initialize contract
    contract = web3.eth.contract(address=address, abi=abi)

    # # Call the contract function
    tx_hash = contract.functions.logTransformation(log, web3.to_checksum_address(owner_addr), img_id).transact({'from': web3.to_checksum_address(sender_addr), 'value': web3.to_wei(0.1, 'ether')})
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print('Updated contract hash: {}'.format(
		tx_hash
	))

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