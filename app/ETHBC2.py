import json
from web3 import Web3

# Fill in your infura API key here
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
web3.eth.default_account = web3.to_checksum_address(
    '0x19c5B3D75ae41aD12253946564A430E0C826fFe3')
print(web3.is_connected())
contract_address = web3.to_checksum_address(
    '0x37D1cFCf48A2B2919bbbd6cA67a1dF5DDe3386F6')
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
				"internalType": "address",
				"name": "arbitrator",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "server",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "stakeAmount",
				"type": "uint256"
			}
		],
		"name": "DisputeResolved",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "arbitrator",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "server",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "stakeAmount",
				"type": "uint256"
			}
		],
		"name": "SuccessResolved",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "percentage",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "resolve_dispute",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "resolve_success",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "server",
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
		"inputs": [],
		"name": "stake",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "stakes",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
''')


def call_stake(senderAddr, stakeAmt):
    # Set a default account to sign transactions - this account is unlocked with Ganache
    print('hello from call_stake')
    sender_addr = web3.to_checksum_address(senderAddr)  # FILL ME IN
    # # Initialize contract
    contract = web3.eth.contract(address=contract_address, abi=abi)
    # # Call the contract function
    em_amt = stakeAmt*0.1
    tx_hash1 = contract.functions.stake().transact(
        {'from': web3.to_checksum_address(sender_addr), 'value': web3.to_wei(stakeAmt, 'ether')})
    web3.eth.wait_for_transaction_receipt(tx_hash1)
    print('Updated contract hash: {}'.format(
        tx_hash1
    ))


def arbitration_success(senderAddr):
    # Set a default account to sign transactions - this account is unlocked with Ganache
    print('hello from arbitration_success')
    sender_addr = web3.to_checksum_address(senderAddr)  # FILL ME IN
    # # Initialize contract
    contract = web3.eth.contract(address=contract_address, abi=abi)
    # # Call the contract function
    tx_hash = contract.functions.resolve_dispute().call(
        {'from': web3.to_checksum_address(sender_addr)})
    # web3.eth.wait_for_transaction_receipt(tx_hash)
    print('Updated contract hash: {}'.format(
        tx_hash
    ))


def arbitration_fail(senderAddr):
    # Set a default account to sign transactions - this account is unlocked with Ganache
    print('hello from arbitration_fail')
    sender_addr = web3.to_checksum_address(senderAddr)  # FILL ME IN
    # # Initialize contract
    contract = web3.eth.contract(address=contract_address, abi=abi)
    # # Call the contract function
    tx_hash = contract.functions.resolve_success().call(
        {'from': web3.to_checksum_address(sender_addr)})
    # web3.eth.wait_for_transaction_receipt(tx_hash)
    print('Updated contract hash: {}'.format(
        tx_hash
    ))


# def unique_img_transact(senderAddr, img_id):
#     # Set a default account to sign transactions - this account is unlocked with Ganache
#     print('hello from unique_img_transact')
#     sender_addr = web3.to_checksum_address(senderAddr)  # FILL ME IN
#     # address = web3.to_checksum_address(
#     #     '0x464ec18f27f6b12919aa8954ED3120302994A528')  # FILL ME IN
#     # # Initialize contract
#     contract = web3.eth.contract(address=contract_address, abi=abi)
#     # # Call the contract function
#     tx_hash = contract.functions.logImageUpload(img_id).transact(
#         {'from': web3.to_checksum_address(sender_addr), 'value': web3.to_wei(0.05, 'ether')})
#     web3.eth.wait_for_transaction_receipt(tx_hash)
#     print('Updated contract hash: {}'.format(
#         tx_hash
#     ))


# # Set a default account to sign transactions - this account is unlocked with Ganache
# # web3.eth.default_account = web3.eth.accounts[0]
# # address = web3.to_checksum_address(
# #     '0x464ec18f27f6b12919aa8954ED3120302994A528')  # FILL ME IN
# # Initialize contract

contract = web3.eth.contract(address=contract_address, abi=abi)
# # Read the default greeting
# x = contract.functions.invest().transact({'value': web3.to_wei(1, 'ether')})
# print(contract.functions.greet().call())
# # # Set a new greeting
# # tx_hash = contract.functions.setGreeting('HEELLLLOOOOOO!!!').transact()
# # # Wait for transaction to be mined
# # web3.eth.waitForTransactionReceipt(tx_hash)
# # # Display the new greeting value
# # print('Updated contract greeting: {}'.format(
# #     contract.functions.greet().call()
# # ))
