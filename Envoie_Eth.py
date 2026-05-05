from web3 import Web3
from os import environ
from user_mapping import user_mapping
from dotenv import load_dotenv
import os

load_dotenv()

# ==========================================================
# CONFIGURATION
# ==========================================================

RPC_URL = "http://10.229.43.182:8545"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print("PRIVATE_KEY manquante")
    exit()
AMOUNT_TO_SEND = 0.1

# ==========================================================
# CONNEXION
# ==========================================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Connexion échouée")
    exit()

print("Connecté à la blockchain")

# ==========================================================
# COMPTE EXPÉDITEUR (AUTO)
# ==========================================================

account = w3.eth.account.from_key(PRIVATE_KEY)
SENDER_ADDRESS = account.address

print(f"Adresse expéditeur : {SENDER_ADDRESS}")

# ==========================================================
# AFFICHER LES SOLDES
# ==========================================================

def afficher_soldes(adresses):
    for adresse in adresses:
        balance_wei = w3.eth.get_balance(adresse)
        balance_eth = w3.from_wei(balance_wei, 'ether')

        nom = user_mapping.get(adresse, "Inconnu")
        print(f"{nom} ({adresse}) : {balance_eth} ETH")

# ==========================================================
# ENVOI DE TRANSACTION
# ==========================================================

def envoyer_eth(destinataire, montant_eth, nonce):

    transaction = {
        "nonce": nonce,
        "to": destinataire,
        "value": w3.to_wei(montant_eth, 'ether'),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 32383
    }

    signed_tx = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return tx_hash.hex()

# ==========================================================
# PROGRAMME PRINCIPAL
# ==========================================================

def main():

    # Toutes les adresses sauf toi
    adresses = [addr for addr in user_mapping.keys() if addr != SENDER_ADDRESS]

    print("\n=== Soldes avant envoi ===")
    afficher_soldes(adresses)

    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

    print("\n=== Envoi des transactions ===")

    for adresse in adresses:
        try:
            tx_hash = envoyer_eth(
                adresse,
                AMOUNT_TO_SEND,
                nonce
            )

            nom = user_mapping.get(adresse, "Inconnu")

            print(f" Envoyé à {nom}")
            print(f"   → {adresse}")
            print(f"   → Hash : {tx_hash}")

            nonce += 1

        except Exception as e:
            print(f"Erreur avec {adresse} : {e}")

    print("\n=== Soldes après envoi ===")
    afficher_soldes(adresses)


# ==========================================================
# LANCEMENT
# ==========================================================

if __name__ == "__main__":
    main()