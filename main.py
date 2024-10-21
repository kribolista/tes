import os
import csv
import json
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime, time

# Load environment variables
load_dotenv()

RPC_URL = os.getenv('RPC_URL')
WETH_CONTRACT_ADDRESS = os.getenv('WETH_CONTRACT_ADDRESS')

# Load WETH ABI
with open('abi.json') as f:
    weth_abi = json.load(f)

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))
weth_contract = web3.eth.contract(address=Web3.toChecksumAddress(WETH_CONTRACT_ADDRESS), abi=weth_abi)

# Load wallets from CSV
def load_wallets():
    wallets = []
    with open('wallets.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            wallets.append(row[0])
    return wallets

# Setup configuration
def setup():
    iterations = int(input("Masukkan jumlah iterasi: "))
    gwei = float(input("Masukkan GWEI untuk gas price (misal 0.075): "))
    min_amount = float(input("Masukkan jumlah minimum yang akan diwrap: "))
    max_amount = float(input("Masukkan jumlah maksimum yang akan diwrap: "))
    schedule_time = input("Masukkan jam untuk jadwal transaksi (HH:MM): ")
    return iterations, gwei, min_amount, max_amount, schedule_time

# Randomize amount to wrap
def random_wrap_amount(min_amount, max_amount):
    return web3.toWei(min_amount + (max_amount - min_amount) * web3.utils.random(), 'ether')

# Execute WETH deposit (wrap)
def wrap_weth(account, amount, gas_price):
    transaction = weth_contract.functions.deposit().buildTransaction({
        'from': account.address,
        'value': amount,
        'gas': 200000,
        'gasPrice': web3.toWei(gas_price, 'gwei'),
        'nonce': web3.eth.getTransactionCount(account.address)
    })
    signed_txn = account.signTransaction(transaction)
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return web3.toHex(tx_hash)

# Execute WETH withdraw (unwrap)
def unwrap_weth(account, gas_price):
    balance = weth_contract.functions.balanceOf(account.address).call()
    if balance > 0:
        transaction = weth_contract.functions.withdraw(balance).buildTransaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': web3.toWei(gas_price, 'gwei'),
            'nonce': web3.eth.getTransactionCount(account.address)
        })
        signed_txn = account.signTransaction(transaction)
        tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return web3.toHex(tx_hash)
    return None

# Main function to execute scheduled transactions
def main():
    wallets = load_wallets()
    iterations, gwei, min_amount, max_amount, schedule_time = setup()
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        if current_time == schedule_time:
            print(f"Running transactions at {current_time}")
            for i in range(iterations):
                for private_key in wallets:
                    account = web3.eth.account.privateKeyToAccount(private_key)
                    # Random wrap amount
                    amount = random_wrap_amount(min_amount, max_amount)
                    # Wrap WETH
                    tx_wrap = wrap_weth(account, amount, gwei)
                    print(f"Wrap Tx: {tx_wrap}")
                    # Unwrap WETH
                    tx_unwrap = unwrap_weth(account, gwei)
                    print(f"Unwrap Tx: {tx_unwrap}")
            break

if __name__ == "__main__":
    main()
