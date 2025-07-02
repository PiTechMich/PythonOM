from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from database import get_conn

def generer_pdf_weasy(mission_id, fichier_sortie="ordre_mission.pdf"):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT objet, lieu, date_depart, duree, moyen_transport, financement FROM mission WHERE id=?", (mission_id,))
    mission = cur.fetchone()

    cur.execute("""SELECT nom, matricule, corps_grade, indice, fonction
                   FROM personnel p
                   JOIN mission_personnel mp ON mp.personnel_id = p.id
                   WHERE mp.mission_id=?""", (mission_id,))
    agents = [{
        "nom": row[0],
        "matricule": row[1],
        "grade": row[2],
        "indice": row[3],
        "fonction": row[4]
    } for row in cur.fetchall()]
    conn.close()

    data = {
        "objet": mission[0],
        "lieu": mission[1],
        "date_depart": mission[2],
        "duree": mission[3],
        "transport": mission[4],
        "financement": mission[5],
        "agents": agents
    }

    # Chargement du modèle
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("ordre_mission.html")
    html_out = template.render(**data)

    # Génération PDF
    HTML(string=html_out, base_url=os.getcwd()).write_pdf(fichier_sortie)
    print(f"✅ PDF généré : {fichier_sortie}")
