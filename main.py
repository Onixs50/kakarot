from web3 import Web3, Account
import json
import os
from dotenv import load_dotenv
from prompt_toolkit import prompt
import time
import random
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor

# Initialize colorama
init()

def save_private_key_to_env(private_keys):
    with open('.env', 'w') as env_file:
        keys_str = json.dumps(private_keys)
        env_file.write(f'PRIVATE_KEYS={keys_str}')

def load_env():
    load_dotenv()

RPC_URL = 'https://sepolia-rpc.kakarot.org'
CHAIN_ID = 1802203764

def generate_random_address():
    return Web3.to_checksum_address(Web3.keccak(os.urandom(20))[:20].hex())

def display_header():
    header = """
    ╔═══════════════════════╗
    ║    Coded By Onixia    ║
    ╚═══════════════════════╝
    """
    print(random.choice([Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]) + header + Style.RESET_ALL)

def get_valid_input(prompt_text, input_type=int):
    while True:
        try:
            return input_type(input(Fore.CYAN + prompt_text + Style.RESET_ALL))
        except ValueError:
            print(Fore.RED + f"Please enter a valid {input_type.__name__}" + Style.RESET_ALL)

def get_valid_float_range(prompt_text):
    while True:
        try:
            values = input(Fore.CYAN + prompt_text + Style.RESET_ALL).split('-')
            return float(values[0]), float(values[1])
        except ValueError:
            print(Fore.RED + "Please enter a valid range (e.g., 0.000001-0.00001)" + Style.RESET_ALL)

def get_valid_int_range(prompt_text):
    while True:
        try:
            values = input(Fore.CYAN + prompt_text + Style.RESET_ALL).split('-')
            return int(values[0]), int(values[1])
        except ValueError:
            print(Fore.RED + "Please enter a valid range (e.g., 1-5)" + Style.RESET_ALL)

def process_wallet(wallet, amount_range, num_addresses, delay_range, provider):
    gas_price = provider.eth.gas_price
    balance = provider.eth.get_balance(wallet.address)
    balance_in_eth = Web3.from_wei(balance, 'ether')
    
    print(Fore.CYAN + f'Wallet {wallet.address} initial balance: {balance_in_eth:.6f} ETH' + Style.RESET_ALL)

    if balance <= 0:
        print(Fore.YELLOW + f'Warning: Wallet {wallet.address} has insufficient balance. Skipping transactions for this wallet.' + Style.RESET_ALL)
        return

    if balance_in_eth < 0.0005:
        print(Fore.YELLOW + f'Warning: Wallet {wallet.address} balance is low: {balance_in_eth:.6f} ETH' + Style.RESET_ALL)

    for _ in range(num_addresses):
        random_address = generate_random_address()
        amount_to_send = random.uniform(*amount_range)
        amount_in_wei = Web3.to_wei(amount_to_send, 'ether')

        tx = {
            'to': random_address,
            'value': amount_in_wei,
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': provider.eth.get_transaction_count(wallet.address),
            'chainId': CHAIN_ID
        }

        try:
            signed_tx = wallet.sign_transaction(tx)
            tx_hash = provider.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(Fore.GREEN + f'Sent {amount_to_send:.8f} ETH from {wallet.address} to {random_address}' + Style.RESET_ALL)
            print(Fore.BLUE + f'Tx Hash: {tx_hash.hex()}' + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f'Failed to send transaction from {wallet.address}: {e}' + Style.RESET_ALL)

        # Random delay between transactions
        delay = random.randint(*delay_range) * 60  # Convert minutes to seconds
        time.sleep(delay)

        # Occasionally print "Coded By Onixia" message
        if random.random() < 0.2:  # 20% chance
            print(random.choice([Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]) + "Coded By Onixia" + Style.RESET_ALL)

def main():
    display_header()

    num_wallets = get_valid_input('How many wallets do you want to use: ', int)
    private_keys = []
    for i in range(num_wallets):
        private_key = input(Fore.CYAN + f'Please enter private key for wallet {i + 1}: ' + Style.RESET_ALL)
        private_keys.append(private_key.strip())
    save_private_key_to_env(private_keys)
    load_env()

    private_keys = json.loads(os.getenv('PRIVATE_KEYS', '[]'))
    provider = Web3(Web3.HTTPProvider(RPC_URL))
    wallets = [Account.from_key(private_key) for private_key in private_keys]

    if not wallets:
        print(Fore.RED + 'No wallets found' + Style.RESET_ALL)
        return

    amount_range = get_valid_float_range('Enter the range of ETH to send (e.g., 0.000001-0.00001): ')
    num_addresses = get_valid_input('How many addresses do you want to send to: ', int)
    delay_range = get_valid_int_range('Enter the delay range between transactions in minutes (e.g., 1-5): ')

    print(Fore.GREEN + "\nTransactions are starting..." + Style.RESET_ALL)

    with ThreadPoolExecutor(max_workers=len(wallets)) as executor:
        futures = [executor.submit(process_wallet, wallet, amount_range, num_addresses, delay_range, provider) for wallet in wallets]
        for future in futures:
            future.result()

if __name__ == '__main__':
    main()
