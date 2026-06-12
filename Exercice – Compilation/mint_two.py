from web3 import Web3
from web3.logs import DISCARD
import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

RPC_URL = "http://10.229.43.182:8545"
CHAIN_ID = 32383
FILE_NAME = "TimmyMarendazNFT"

CONTRACT_ADDRESS = "0xD004598EB796265c05ba741C789B39370A52978e"

MY_ADDRESS = os.getenv("MY_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not MY_ADDRESS or not PRIVATE_KEY:
    raise Exception("MY_ADDRESS ou PRIVATE_KEY manquant → vérifie le .env à côté du script")

# Les deux NFT à minter
URLS = [
    "https://raw.githubusercontent.com/Catwood5/I107/refs/heads/main/%20Exercice-Fil-Rouge/NFT.json",
    "https://raw.githubusercontent.com/Catwood5/I107/refs/heads/main/%20Exercice-Fil-Rouge/NFT2.json",
]

# --- Vérification des URLs AVANT de minter (l'URI est gravée à jamais) ---
print("Vérification des URLs…")
for url in URLS:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = r.read()
    except Exception as e:
        raise Exception(f"URL inaccessible : {url}\n→ {e}\n→ Pousse le fichier sur GitHub avant de minter !")
    if url.lower().endswith(".json"):
        meta = json.loads(data.decode())
        img = meta.get("image")
        if not img:
            raise Exception(f"Pas de champ 'image' dans {url}")
        req = urllib.request.Request(img, method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                pass
        except Exception as e:
            raise Exception(f"Image inaccessible : {img}\n→ {e}\n→ Corrige le champ 'image' du JSON ou pousse l'image !")
        print(f"  ✅ {meta.get('name', '?')} — JSON et image OK")
    else:
        print(f"  ✅ {url} accessible")

# --- Connexion ---
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Erreur : impossible de se connecter à la blockchain")

sender = w3.to_checksum_address(MY_ADDRESS)
contract_address = w3.to_checksum_address(CONTRACT_ADDRESS)

if len(w3.eth.get_code(contract_address)) <= 2:
    raise Exception("Aucun contrat à cette adresse — vérifie CONTRACT_ADDRESS")

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, FILE_NAME + ".abi"), "r") as f:
    abi = json.load(f)
contract = w3.eth.contract(address=contract_address, abi=abi)

if not contract.functions.isMintEnabled().call():
    raise Exception("Mint pas activé")

print(f"\nÉtat : {contract.functions.totalSupply().call()}/{contract.functions.maxSupply().call()} mintés, "
      f"{contract.functions.mintedWallets(sender).call()}/2 par ce wallet")

# --- Mint des deux NFT ---
for i, url in enumerate(URLS, 1):
    print(f"\n--- Mint {i}/{len(URLS)} ---")
    tx = contract.functions.mint(url).build_transaction({
        "chainId": CHAIN_ID,
        "from": sender,
        "value": w3.to_wei(0.05, "ether"),
        "gas": 300000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "nonce": w3.eth.get_transaction_count(sender),
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("Tx :", w3.to_hex(tx_hash))
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt.status == 0:
        raise Exception(f"Mint {i} revert — un require() du contrat a échoué")
    token_id = contract.events.Transfer().process_receipt(receipt, errors=DISCARD)[0]["args"]["tokenId"]
    print(f"✅ Token ID {token_id} minté | bloc {receipt.blockNumber}")
    print("   Owner :", contract.functions.ownerOf(token_id).call())
    print("   URI   :", contract.functions.tokenURI(token_id).call())

print("\n" + "=" * 60)
print("MINT TERMINE — Import Metamask :")
print("  Address  :", CONTRACT_ADDRESS)
print("  Token ID : 1, puis refais l'import avec 2")
print("=" * 60)