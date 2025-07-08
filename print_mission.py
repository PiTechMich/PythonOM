from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import date
import os
from database import get_conn

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

    # Création d'un seul canvas PDF
    c = canvas.Canvas(chemin, pagesize=A4)
    largeur, hauteur = A4

    for i, agent in enumerate(agents):
        # --- LOGO PRÉSIDENCE CENTRÉ EN HAUT ---
        logo_presidence = os.path.join(os.path.dirname(__file__), "static", "logo_presidence.png")
        if os.path.isfile(logo_presidence):
            c.drawImage(logo_presidence, (largeur - 5*cm)/2, hauteur - 4*cm, width=5*cm, height=5*cm, preserveAspectRatio=True)

        # --- LOGO MEN à gauche + hiérarchie ---
        logo_men = os.path.join(os.path.dirname(__file__), "static", "logo_ministere.png")
        if os.path.isfile(logo_men):
            c.drawImage(logo_men, 3.5*cm, hauteur - 4.5*cm, width=2*cm, height=2*cm, preserveAspectRatio=True)

        # --- Texte hiérarchique à gauche ---
        x_center = 3.5*cm + 1.5*cm
        y_text = hauteur - 5.3*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x_center, y_text, "Ministère de l'Éducation Nationale")
        y_text -= 0.5*cm
        c.setFont("Helvetica", 12)
        c.drawCentredString(x_center, y_text, "★ " * 6)
        y_text -= 0.6*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x_center, y_text, "Secrétariat Général")
        y_text -= 0.5*cm
        c.setFont("Helvetica", 12)
        c.drawCentredString(x_center, y_text, "★ " * 6)
        y_text -= 0.6*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x_center, y_text, "Direction du Patrimoine Foncier")
        y_text -= 0.5*cm
        c.drawCentredString(x_center, y_text, "et des Infrastructures")
        y_text -= 0.8*cm
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(x_center, y_text, "N° 2025-....../MEN/SG/DPFI")

        # --- Partie droite : Date + Titre
        c.setFont("Helvetica", 10)
        c.drawRightString(largeur - 2*cm, hauteur - 5*cm, f"Antananarivo, le {date.today().strftime('%d/%m/%Y')}")
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(largeur - 2*cm, hauteur - 8*cm, "ORDRE DE MISSION")

        # --- Corps du document ---
        y = hauteur - 10.5*cm
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, y, "Il est ordonné à :")
        y -= 0.8*cm

        # --- Infos missionnaire avec indentation propre ---
        infos_agent = [
            ("Nom et Prénom", agent[0]),
            ("IM", agent[1]),
            ("Corps et Grade", agent[2]),
            ("Indice", str(agent[3])),
            ("Fonction", agent[4]),
        ]
        for label, value in infos_agent:
            c.drawString(3*cm, y, f"{label} : {value}")
            y -= 0.7*cm

        y -= 0.5*cm
        c.setFont("Helvetica", 12)
        mission_infos = [
            ("De se rendre à", mission[1]),
            ("Motif du déplacement", mission[0]),
            ("Date de départ", mission[2]),
            ("Durée", str(mission[3]) + " jour(s)"),
            ("Moyen de transport", mission[4]),
        ]
        for label, value in mission_infos:
            c.drawString(3*cm, y, f"{label} : {value}")
            y -= 0.7*cm

        # --- Clôture ---
        y -= 1.2*cm
        c.drawString(2*cm, y, "Le présent ordre de mission lui est délivré pour servir et valoir ce que de droit.")

        # Signature
        y -= 2*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(largeur - 2*cm, y, "Visa du Responsable")

        c.showPage()

    c.save()
    conn.close()
    print(f"✅ PDF multi-pages aligné généré dans : {chemin}")
