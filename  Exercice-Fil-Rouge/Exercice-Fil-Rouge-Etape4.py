from web3 import Web3
import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

RPC_URL = "http://10.229.43.182:8545"
CHAIN_ID = 32383

CONTRACT_ADDRESS = "0x230DC51031AC30C056855155Bf2BBFA75abEe475"

MY_ADDRESS = os.getenv("MY_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

NFT_METADATA_URL = "https://raw.githubusercontent.com/Catwood5/I107/refs/heads/main/%20Exercice-Fil-Rouge/NFT.json"

# --- Vérification des métadonnées AVANT de minter (l'URI est gravée à jamais !) ---
print("Vérification des métadonnées…")
try:
    with urllib.request.urlopen(NFT_METADATA_URL, timeout=10) as r:
        metadata = json.loads(r.read().decode())
except Exception as e:
    raise Exception(f"Le JSON de métadonnées est inaccessible : {e}")

image_url = metadata.get("image")
if not image_url:
    raise Exception("Le JSON n'a pas de champ 'image' → Metamask n'affichera rien")

try:
    req = urllib.request.Request(image_url, method="HEAD")
    with urllib.request.urlopen(req, timeout=10) as r:
        if r.status != 200:
            raise Exception(f"HTTP {r.status}")
except Exception as e:
    raise Exception(
        f"L'image référencée dans le JSON est inaccessible ({e}) :\n{image_url}\n"
        "→ Corrige le champ 'image' dans NFT.json (le chemin doit contenir %20) et push avant de minter !"
    )

print(f"JSON OK — name: {metadata.get('name')}")
print(f"Image OK — {image_url}")

# --- Connexion ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Erreur : impossible de se connecter à la blockchain")

sender_address = w3.to_checksum_address(MY_ADDRESS)
contract_address = w3.to_checksum_address(CONTRACT_ADDRESS)

# --- Diagnostic : le contrat existe-t-il vraiment ? ---
if len(w3.eth.get_code(contract_address)) <= 2:
    raise Exception("Aucun contrat à cette adresse sur le réseau CPNV.")

# --- Chargement de l'ABI ---
abi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SimpleMintContract.abi")
with open(abi_path, "r") as abi_file:
    contract_abi = json.load(abi_file)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# --- Vérifications avant d'envoyer ---
if not contract.functions.isMintEnabled().call():
    raise Exception("Mint pas activé → demander au formateur")
if contract.functions.totalSupply().call() >= contract.functions.maxSupply().call():
    raise Exception("Sold out → demander au formateur d'augmenter maxSupply")
if contract.functions.mintedWallets(sender_address).call() >= 1:
    raise Exception("Ce wallet a déjà minté sur CE contrat → utilise la 3e adresse (0xb5913CF6...)")

# --- Mint ---
nonce = w3.eth.get_transaction_count(sender_address)

transaction = contract.functions.mint(NFT_METADATA_URL).build_transaction({
    "chainId": CHAIN_ID,
    "from": sender_address,
    "value": w3.to_wei(0.05, "ether"),
    "gas": 300000,
    "gasPrice": w3.to_wei("20", "gwei"),
    "nonce": nonce,
})

signed_tx = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("\nTransaction envoyée :", w3.to_hex(tx_hash))

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
if receipt.status == 0:
    raise Exception("Transaction revert : un require() du contrat a échoué")

from web3.logs import DISCARD
token_id = contract.events.Transfer().process_receipt(receipt, errors=DISCARD)[0]["args"]["tokenId"]

print("\nNFT minté avec succès !")
print("Bloc     :", receipt.blockNumber)
print("Token ID :", token_id)
print("Owner    :", contract.functions.ownerOf(token_id).call())
print("URI      :", contract.functions.tokenURI(token_id).call())
print("\n→ Import Metamask : Address =", CONTRACT_ADDRESS, "| Token ID =", token_id)