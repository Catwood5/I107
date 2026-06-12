from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

RPC_URL = "http://10.229.43.182:8545"
CHAIN_ID = 32383
FILE_NAME = "TimmyMarendazNFT"

MY_ADDRESS = os.getenv("MY_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# --- Connexion ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Erreur : impossible de se connecter à la blockchain")

sender = w3.to_checksum_address(MY_ADDRESS)
print("Déployeur :", sender)
print("Solde     :", w3.from_wei(w3.eth.get_balance(sender), "ether"), "ETH")

# --- Chargement ABI + bytecode (chemins relatifs au script) ---
base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, FILE_NAME + ".abi"), "r") as f:
    abi = json.load(f)
with open(os.path.join(base, FILE_NAME + ".bin"), "r") as f:
    bytecode = "0x" + f.read().strip()

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# --- Déploiement (le constructeur prend ton adresse comme owner) ---
print("\nDéploiement en cours…")
tx = Contract.constructor(sender).build_transaction({
    "chainId": CHAIN_ID,
    "from": sender,
    "gas": 3000000,
    "gasPrice": w3.to_wei("20", "gwei"),
    "nonce": w3.eth.get_transaction_count(sender),
})
signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
if receipt.status == 0:
    raise Exception("Déploiement revert !")

contract_address = receipt.contractAddress
print("Contrat déployé à :", contract_address)

# --- Activation du mint (tu es owner, donc tu peux) ---
contract = w3.eth.contract(address=contract_address, abi=abi)
print("\nActivation du mint…")
tx2 = contract.functions.toggleIsMintEnabled().build_transaction({
    "chainId": CHAIN_ID,
    "from": sender,
    "gas": 100000,
    "gasPrice": w3.to_wei("20", "gwei"),
    "nonce": w3.eth.get_transaction_count(sender),
})
signed2 = w3.eth.account.sign_transaction(tx2, PRIVATE_KEY)
r2 = w3.eth.wait_for_transaction_receipt(
    w3.eth.send_raw_transaction(signed2.raw_transaction)
)
if r2.status == 0:
    raise Exception("Activation du mint revert !")

# --- Récapitulatif ---
print("\n" + "=" * 60)
print("DEPLOIEMENT TERMINE")
print("=" * 60)
print("Adresse du contrat :", contract_address)
print("Nom du token       :", contract.functions.name().call())
print("Symbole            :", contract.functions.symbol().call())
print("Mint activé        :", contract.functions.isMintEnabled().call())
print("Max supply         :", contract.functions.maxSupply().call())
print("Owner              :", contract.functions.owner().call())
print("=" * 60)
print("\n1) Envoie cette adresse au formateur sur Teams")
print("   (Timmy Marendaz + numéro de groupe)")
print("2) Copie-la dans CONTRACT_ADDRESS de mint_two.py")
