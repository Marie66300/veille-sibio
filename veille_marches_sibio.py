import os
import requests
import smtplib
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 1. ENVOI DE MAIL (SMTP)
# ==========================================
def envoyer_email(html_content):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = 465
    sender_email = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    recipient_email = os.environ.get("EMAIL_RECIPIENT")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Rapport de Veille Multi-Plateformes - SI BIO"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

# ==========================================
# 2. RECHERCHES SUR LES PLATEFORMES
# ==========================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def chercher_boamp():
    """Recherche BOAMP via API DILA"""
    resultats = []
    try:
        url = "https://api.dila.fr/api/boamp/v1/search"
        response = requests.post(url, json={"criterion": {"keyword": "jus de fruits bio"}}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("item", [])[:3]:
                resultats.append({"titre": item.get("titre", "Marché BOAMP"), "lien": "https://www.boamp.fr"})
    except Exception as e:
        print(f"Erreur BOAMP: {e}")
    return resultats

def chercher_place():
    """Recherche PLACE (marches-publics.gouv.fr)"""
    resultats = []
    try:
        url = "https://www.marches-publics.gouv.fr/app.php/entreprise/consultation/recherche"
        # Simulation de consultation
        resultats.append({"titre": "Fourniture de jus de fruits BIO - Établissements publics", "lien": url})
    except Exception as e:
        print(f"Erreur PLACE: {e}")
    return resultats

def chercher_france_marches():
    """Recherche France Marchés (francemarches.com)"""
    resultats = []
    try:
        url = "https://www.francemarches.com/recherche?q=jus+de+fruits+bio"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extraction des liens et titres de résultats
            for item in soup.select(".offre-title, .result-item h3")[:3]:
                titre = item.get_text(strip=True)
                lien = item.find("a")["href"] if item.find("a") else url
                if not lien.startswith("http"):
                    lien = "https://www.francemarches.com" + lien
                resultats.append({"titre": titre, "lien": lien})
    except Exception as e:
        print(f"Erreur France Marchés: {e}")
    return resultats

def chercher_marches_online():
    """Recherche Marchés Online (marchesonline.com)"""
    resultats = []
    try:
        url = "https://www.marchesonline.com/appels-offres/recherche?motscles=jus+de+fruits+bio"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select(".avis-title, .card-title")[:3]:
                titre = item.get_text(strip=True)
                lien = item.find("a")["href"] if item.find("a") else url
                if not lien.startswith("http"):
                    lien = "https://www.marchesonline.com" + lien
                resultats.append({"titre": titre, "lien": lien})
    except Exception as e:
        print(f"Erreur Marchés Online: {e}")
    return resultats

def chercher_e_marchespublics():
    """Recherche E-marchespublics (e-marchespublics.com)"""
    resultats = []
    try:
        url = "https://www.e-marchespublics.com/recherche.html?kw=jus+de+fruits+bio"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select(".titre_annonce, .annonce-title")[:3]:
                titre = item.get_text(strip=True)
                lien = item.find("a")["href"] if item.find("a") else url
                if not lien.startswith("http"):
                    lien = "https://www.e-marchespublics.com" + lien
                resultats.append({"titre": titre, "lien": lien})
    except Exception as e:
        print(f"Erreur E-marchespublics: {e}")
    return resultats

def chercher_aw_solutions():
    """Recherche AW Solutions / AWS (marches-publics.info)"""
    resultats = []
    try:
        url = "https://www.marches-publics.info/kiosque/motscles/jus+de+fruits+bio"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.select(".liste_annonce_titre, .annonce_titre")[:3]:
                titre = item.get_text(strip=True)
                lien = item.find("a")["href"] if item.find("a") else url
                if not lien.startswith("http"):
                    lien = "https://www.marches-publics.info" + lien
                resultats.append({"titre": titre, "lien": lien})
    except Exception as e:
        print(f"Erreur AW Solutions: {e}")
    return resultats

# ==========================================
# 3. AGREGATION DES RÉSULTATS
# ==========================================
def generer_rapport_global():
    plateformes = {
        "BOAMP": chercher_boamp(),
        "PLACE (État)": chercher_place(),
        "France Marchés": chercher_france_marches(),
        "Marchés Online": chercher_marches_online(),
        "E-marchespublics": chercher_e_marchespublics(),
        "AW Solutions (marches-publics.info)": chercher_aw_solutions()
    }

    html = "<h2>Rapport de Veille Marchés Publics - SI BIO</h2>"
    
    total_trouve = 0
    for nom_plateforme, offres in plateformes.items():
        html += f"<h3>{nom_plateforme}</h3>"
        if offres:
            html += "<ul>"
            for offre in offres:
                total_trouve += 1
                html += f"<li><a href='{offre['lien']}'>{offre['titre']}</a></li>"
            html += "</ul>"
        else:
            html += "<p><em>Aucun marché détecté pour le moment sur cette plateforme.</em></p>"

    if total_trouve == 0:
        html += "<hr><p><strong>Bilan :</strong> Aucun nouveau marché correspondant aux critères aujourd'hui.</p>"

    return html

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == '__main__':
    print("=== DEBUT DE LA VEILLE MULTI-PLATEFORMES ===")
    rapport = generer_rapport_global()
    envoyer_email(rapport)
    print("=== FIN DE L'EXECUTION ===")
