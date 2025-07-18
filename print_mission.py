from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import date
import os
import sys
import subprocess
from num2words import num2words

from PyQt5.QtWidgets import QFileDialog
from database import get_conn

def choisir_chemin_pdf(parent=None):
    chemin, _ = QFileDialog.getSaveFileName(parent, "Enregistrer l'ordre de mission", "ordre_mission.pdf", "PDF Files (*.pdf)")
    return chemin

def ouvrir_pdf(chemin):
    try:
        if sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', chemin])
        elif sys.platform.startswith('win'):
            os.startfile(chemin)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', chemin])
    except Exception as e:
        print(f"Erreur lors de l'ouverture du PDF : {e}")

def generer_pdf_reportlab(mission_id, chemin="ordre_mission.pdf"):
    conn = get_conn()
    cur = conn.cursor()

    # --- Récupération mission ---
    cur.execute("SELECT objet, lieu, date_depart, duree, moyen_transport, financement FROM mission WHERE id=?", (mission_id,))
    mission = cur.fetchone()

    # --- Récupération missionnaires ---
    cur.execute("""SELECT nom, matricule, corps_grade, indice, fonction
                   FROM personnel p
                   JOIN mission_personnel mp ON mp.personnel_id = p.id
                   WHERE mp.mission_id=?""", (mission_id,))
    agents = cur.fetchall()

    c = canvas.Canvas(chemin, pagesize=A4)
    largeur, hauteur = A4

    for i, agent in enumerate(agents):
        # Entête et logos
        logo_presidence = os.path.join(os.path.dirname(__file__), "static", "logo_presidence.png")
        if os.path.isfile(logo_presidence):
            c.drawImage(logo_presidence, (largeur - 5*cm)/2, hauteur - 4*cm, width=5*cm, height=5*cm, preserveAspectRatio=True)

        logo_men = os.path.join(os.path.dirname(__file__), "static", "logo_ministere.png")
        if os.path.isfile(logo_men):
            c.drawImage(logo_men, 3.5*cm, hauteur - 4.5*cm, width=2*cm, height=2*cm, preserveAspectRatio=True)

        x_center = 3.5*cm + 1.5*cm
        y_text = hauteur - 5.3*cm
        c.setFont("Helvetica", 11)
        c.drawCentredString(x_center, y_text, "Ministère de l'Éducation Nationale")
        y_text -= 0.5*cm
        c.setFont("Helvetica", 12)
        c.drawCentredString(x_center, y_text, "- " * 6)
        y_text -= 0.6*cm
        c.setFont("Helvetica", 11)
        c.drawCentredString(x_center, y_text, "Secrétariat Général")
        y_text -= 0.5*cm
        c.setFont("Helvetica", 12)
        c.drawCentredString(x_center, y_text, "- " * 6)
        y_text -= 0.6*cm
        c.setFont("Helvetica", 11)
        c.drawCentredString(x_center, y_text, "Direction du Patrimoine Foncier")
        y_text -= 0.5*cm
        c.drawCentredString(x_center, y_text, "et des Infrastructures")
        y_text -= 0.8*cm
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(x_center, y_text, "N° 2025- ........./ MEN / SG / DPFI")

        # Droite : Date + titre
        c.setFont("Helvetica", 10)
        c.drawString(largeur - 8*cm, hauteur - 5*cm, "Antananarivo, le")
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(largeur - 2*cm, hauteur - 8*cm, "ORDRE DE MISSION")

        # Corps du document
        y = hauteur - 10.5*cm
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, y, "Il est ordonné à :")
        y -= 0.8*cm

        label_x = 3*cm
        value_x = 9.5*cm

        infos_agent = [
            ("Nom et Prénom", agent[0]),
            ("IM", "{:,}".format(int(agent[1])).replace(",", " ") if str(agent[1]).isdigit() else agent[1]),
            ("Corps et Grade", agent[2]),
            ("Indice", "{:,}".format(int(agent[3])).replace(",", " ") if str(agent[3]).isdigit() else agent[3]),
            ("Fonction", agent[4]),
        ]
        for label, value in infos_agent:
            c.drawString(label_x, y, label)
            c.drawString(value_x, y, f": {value}")
            y -= 0.7*cm

        #y -= 0.5*cm
        mission_infos = [
            ("De se rendre à", mission[1]),
            ("Motif de déplacement", mission[0]),
            ("Date de départ", date.fromisoformat(mission[2]).strftime("%d/%m/%Y") if isinstance(mission[2], str) else mission[2].strftime("%d/%m/%Y")),
            ("Durée de déplacement", f"{num2words(mission[3], lang='fr')} ({mission[3]}) jour{'s' if mission[3] > 1 else ''}"),
            ("Moyen de transport", mission[4]),
        ]
        for label, value in mission_infos:
            c.drawString(label_x, y, label)
            c.drawString(value_x, y, f": {value}")
            y -= 0.7*cm

        y -= 1.2*cm
        c.drawString(2*cm, y, "Le présent ordre de mission lui est délivré pour servir et valoir ce que de droit.")

        #y -= 2*cm
        #c.setFont("Helvetica-Bold", 11)
        #c.drawRightString(largeur - 2*cm, y, "Visa du Responsable")

        c.showPage()

    c.save()
    conn.close()
    print(f"✅ PDF généré dans : {chemin}")
