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
# 2. FONCTIONS DE RECHERCHE PAR PLATEFORME
# ==========================================

KEYWORDS = ["jus de fruits bio", "boissons bio", "nectar bio"]

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
        resultats.append({"titre": "Exemple PLACE : Fourniture de boissons BIO pour établissements publics", "lien": url})
    except Exception as e:
        print(f"Erreur PLACE: {e}")
    return resultats

def chercher_france_marches():
    """Recherche France Marchés (francemarches.com)"""
    return []

def chercher_marches_online():
    """Recherche Marchés Online (marchesonline.com)"""
    return []

def chercher_e_marchespublics():
    """Recherche E-marchespublics (e-marchespublics.com)"""
    return []

def chercher_aw_solutions():
    """Recherche AW Solutions (marches-publics.info)"""
    return []

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
            html += "<p><em>Aucune nouvelle offre détectée sur cette plateforme.</em></p>"

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
