import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION SIBIO ---
CATALOGUE_KEYWORDS = [
    "jus de fruit",
    "jus bio",
    "nectar",
    "citronnade",
    "confiture bio",
    "puree de fruits",
    "soupe bio",
    "gaspacho",
    "boisson bio",
    "restauration scolaire jus",
]

# Email pour recevoir les alerte
EMAIL_EXPEDITEUR = "votre_email@si-bio.fr"
EMAIL_MOT_DE_PASSE = "votre_mot_de_passe_application"
EMAIL_DESTINATAIRE = "commercial@si-bio.fr"


def inspecter_boamp():
    """Interroge l'API officielle du BOAMP pour les marchés de boissons/alimentation bio"""
    url = "https://une-statistique-boamp.dila.fr/api/peer/v1.0/search"
    # Recherche sur les CPV Aliments et boissons (15800000, 15300000)
    query = "bio AND (jus OR nectar OR boisson OR confiture)"

    params = {
        "q": query,
        "page": 0,
        "size": 20,
        "sort": "dateParution,desc",
    }

    resultats = []
    try:
        response = requests.get(
            "https://dila-api.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records",
            params={
                "where": 'search(objet, "jus") OR search(objet, "boisson") OR search(objet, "nectar")',
                "limit": 10,
            },
        )
        if response.status_code == 200:
            data = response.json()
            for record in data.get("results", []):
                resultats.append(
                    {
                        "source": "BOAMP",
                        "titre": record.get("objet", "Sans titre"),
                        "acheteur": record.get("nomacheteur", "Non spécifié"),
                        "date_limite": record.get("datelimitereponse", "N/C"),
                        "lien": record.get("url_avis", "#"),
                    }
                )
    except Exception as e:
        print(f"Erreur lors de l'inspection BOAMP: {e}")

    return resultats


def inspecter_aji():
    """Scrape les avis récents sur la plateforme AJI Éducation"""
    url = "https://mapa.aji-france.com"
    resultats = []
    # Simulation de structure de recherche sur AJI
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(
            f"{url}/liste-mapa?keywords=jus+bio", headers=headers, timeout=10
        )
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # Extraction dynamique selon les éléments de la plateforme
            for item in soup.select(".offre-item, .card-mapa")[
                :5
            ]:  # adapter les sélecteurs
                titre = item.select_one(".titre").get_text(strip=True)
                link = url + item.select_one("a")["href"]
                resultats.append(
                    {
                        "source": "AJI Éducation",
                        "titre": titre,
                        "acheteur": "Établissement Scolaire",
                        "date_limite": "Voir fiche",
                        "lien": link,
                    }
                )
    except Exception as e:
        print(f"Erreur lors de l'inspection AJI: {e}")

    return resultats


def generer_rapport_html(opportunites):
    """Génère le corps de l'email au format HTML"""
    if not opportunites:
        return "<p>Aucun nouvel appel d'offres correspondant au catalogue SIBIO n'a été trouvé cette fois-ci.</p>"

    html = """
    <h2>Veille Automatique Marchés Publics - SI BIO</h2>
    <p>Voici les opportunités détectées lors de l'inspection automatique :</p>
    <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #4CAF50; color: white;">
            <th>Source</th>
            <th>Objet du marché</th>
            <th>Acheteur</th>
            <th>Date Limite</th>
            <th>Lien</th>
        </tr>
    """
    for opp in opportunites:
        html += f"""
        <tr>
            <td><b>{opp['source']}</b></td>
            <td>{opp['titre']}</td>
            <td>{opp['acheteur']}</td>
            <td>{opp['date_limite']}</td>
            <td><a href="{opp['lien']}">Consulter l'offre</a></td>
        </tr>
        """
    html += "</table>"
    return html


def envoyer_email(contenu_html):
    """Envoie le récapitulatif par email"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🥤 [Veille SIBIO] Nouveaux marchés publics détectés"
    msg["From"] = EMAIL_EXPEDITEUR
    msg["To"] = EMAIL_DESTINATAIRE

    msg.attach(MIMEText(contenu_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_EXPEDITEUR, EMAIL_MOT_DE_PASSE)
        server.sendmail(EMAIL_EXPEDITEUR, EMAIL_DESTINATAIRE, msg.as_string())


def job_veille():
    print("Démarrage de la veille marchés publics SIBIO...")
    offres = []
    offres.extend(inspecter_boamp())
    offres.extend(inspecter_aji())

    html_report = generer_rapport_html(offres)
    envoyer_email(html_report)
    print("Veille terminée et email envoyé avec succès !")


if __name__ == "__main__":
    job_veille()
