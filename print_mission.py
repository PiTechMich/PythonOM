from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from database import get_conn
import os

def generer_pdf_reportlab(mission_id, chemin="ordre_mission.pdf"):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT objet, lieu, date_depart, duree, moyen_transport, financement FROM mission WHERE id=?", (mission_id,))
    mission = cur.fetchone()

    cur.execute("""SELECT nom, matricule, corps_grade, indice, fonction
                   FROM personnel p
                   JOIN mission_personnel mp ON mp.personnel_id = p.id
                   WHERE mp.mission_id=?""", (mission_id,))
    agents = cur.fetchall()

    for i, agent in enumerate(agents):
        page_file = f"{chemin.replace('.pdf', '')}_{i+1}.pdf"
        c = canvas.Canvas(page_file, pagesize=A4)
        c.setFont("Helvetica-Bold", 14)

        # En-tête
        logo_path = os.path.join(os.path.dirname(__file__), "static", "logo_ministere.png")
        if not os.path.isfile(logo_path):
            raise FileNotFoundError(f"Logo introuvable : {logo_path}")
        c.drawImage(logo_path, 2*cm, 26*cm, width=4*cm, height=4*cm, preserveAspectRatio=True, mask='auto')
        c.drawString(6*cm, 27*cm, "MINISTÈRE DE ...")
        c.setFont("Helvetica", 12)
        c.drawString(6*cm, 26.3*cm, "ORDRE DE MISSION")

        # Infos mission
        y = 24*cm
        infos = [
            ("Objet", mission[0]),
            ("Lieu", mission[1]),
            ("Date départ", mission[2]),
            ("Durée", str(mission[3])),
            ("Moyen de transport", mission[4]),
            ("Financement", mission[5]),
        ]
        for label, value in infos:
            c.drawString(2*cm, y, f"{label} : {value}")
            y -= 1*cm

        # Infos agent
        y -= 1*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "Informations de l'agent")
        y -= 0.7*cm
        c.setFont("Helvetica", 12)
        agent_infos = [
            ("Nom", agent[0]),
            ("Matricule", agent[1]),
            ("Corps/Grade", agent[2]),
            ("Indice", str(agent[3])),
            ("Fonction", agent[4])
        ]
        for label, value in agent_infos:
            c.drawString(2*cm, y, f"{label} : {value}")
            y -= 0.7*cm

        # Signature
        y -= 2*cm
        c.drawString(12*cm, y, "Visa Responsable")
        c.showPage()
        c.save()

    conn.close()
    print("✅ PDF généré(s) avec ReportLab.")
