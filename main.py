import os
import csv
import random
import asyncio
import schedule
import time
from dotenv import load_dotenv
from web3 import Web3

# Load .env file
load_dotenv()

# Koneksi ke jaringan Taiko
w3 = Web3(Web3.HTTPProvider('https://rpc.taiko.network'))

# Load private keys dari .env
wallet1_pk = os.getenv("WALLET1_PK")
wallet2_pk = os.getenv("WALLET2_PK")

# Fungsi membaca wallet dari CSV (optional)
def load_wallets_from_csv(filename):
    wallets = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            wallets.append({
                'private_key': row['private_key'],
                'address': row['address']
            })
    return wallets

# Fungsi wrap
def wrap(wallet_pk, amount, gas_price):
    wallet = w3.eth.account.privateKeyToAccount(wallet_pk)
    print(f'Wrapping {amount} ETH for wallet {wallet.address} with gas price {gas_price} Gwei')
    # Implementasi transaksi wrap

# Fungsi unwrap
def unwrap(wallet_pk, gas_price):
    wallet = w3.eth.account.privateKeyToAccount(wallet_pk)
    balance = w3.eth.get_balance(wallet.address)
    print(f'Unwrapping {balance} ETH for wallet {wallet.address} with gas price {gas_price} Gwei')
    # Implementasi transaksi unwrap

# Fungsi transaksi paralel
async def parallel_transactions(wallets, iterations, min_amount, max_amount, gas_price):
    loop = asyncio.get_event_loop()
    for i in range(iterations):
        tasks = []
        for wallet in wallets:
            wrap_amount = random.uniform(min_amount, max_amount)
            tasks.append(loop.run_in_executor(None, wrap, wallet['private_key'], wrap_amount, gas_price))
            tasks.append(loop.run_in_executor(None, unwrap, wallet['private_key'], gas_price))
        await asyncio.gather(*tasks)

# Konfigurasi awal
def setup():
    iterations = int(input("Masukkan jumlah iterasi: "))
    gwei = int(input("Masukkan GWEI untuk gas price: "))
    min_amount = float(input("Masukkan jumlah minimum wrap: "))
    max_amount = float(input("Masukkan jumlah maksimum wrap: "))
    schedule_time = input("Masukkan waktu untuk transaksi (format HH:MM): ")
    return iterations, gwei, min_amount, max_amount, schedule_time

# Fungsi terjadwal
def scheduled_job(wallets):
    iterations, gwei, min_amount, max_amount, _ = setup()
    asyncio.run(parallel_transactions(wallets, iterations, min_amount, max_amount, gwei))

# Setup dan scheduling
iterations, gwei, min_amount, max_amount, schedule_time = setup()

# Menjadwalkan transaksi sesuai waktu input user
wallets = load_wallets_from_csv('wallets.csv')  # Alternatif: gunakan wallet1_pk, wallet2_pk dari .env
schedule.every().day.at(schedule_time).do(scheduled_job, wallets)

# Main loop untuk schedule
while True:
    schedule.run_pending()
    time.sleep(60)
