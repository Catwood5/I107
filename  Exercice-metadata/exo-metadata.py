from web3 import Web3
from dotenv import load_dotenv
import os
import json

# ==================================================
# CHARGEMENT VARIABLES ENVIRONNEMENT
# ==================================================

load_dotenv()

RPC_URL = "http://10.229.43.182:8545"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print("PRIVATE_KEY manquante dans le fichier .env")
    exit()

# ==================================================
# CONNEXION BLOCKCHAIN
# ==================================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Connexion échouée")
    exit()

print("Connecté à la blockchain")

# ==================================================
# COMPTE EXPEDITEUR
# ==================================================

account = w3.eth.account.from_key(PRIVATE_KEY)
sender = account.address

print("Adresse expéditeur :", sender)

# ==================================================
# CREATION DES METADONNEES
# ==================================================


with open("data.json", "r") as f:
    data = json.load(f)

# codage des données
metadata_hex = w3.to_hex(text=json.dumps(data))

# ==================================================
# CREATION TRANSACTION
# ==================================================

nonce = w3.eth.get_transaction_count(sender)

transaction = {
    "nonce": nonce,
    "to": sender,
    "value": 0,
    "gas": 200000,
    "gasPrice": w3.eth.gas_price,
    "chainId": 32383,
    "data": w3.to_hex(text=metadata_hex)
}

# ==================================================
# SIGNATURE TRANSACTION
# ==================================================

signed_tx = w3.eth.account.sign_transaction(
    transaction,
    PRIVATE_KEY
)



