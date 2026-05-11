import hashlib

print("Choisissez une option :")
print("[1] texte")
print("[2] fichier")

choix = input("choix : ")

if choix == "1":
    texte = input("Entrez le texte à hacher : ")
    hash_resultat = hashlib.sha256(texte.encode()).hexdigest()
    print("SHA-256 :", hash_resultat)

elif choix == "2":
    chemin = input("Entrez le chemin du fichier : ")
    fichier = open(chemin, "rb")
    contenu = fichier.read()
    fichier.close()
    hash_resultat = hashlib.sha256(contenu).hexdigest()
    print("SHA-256 :", hash_resultat)

else:
    print("Option invalide")

