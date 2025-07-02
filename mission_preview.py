import os
from jinja2 import Environment, FileSystemLoader
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from database import get_conn

class ApercuMission(QWidget):
    def __init__(self, mission_id):
        super().__init__()
        self.setWindowTitle("Aperçu de la mission")
        self.setMinimumSize(800, 600)
        self.mission_id = mission_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.view = QWebEngineView()
        self.btn_export = QPushButton("Exporter en PDF")
        self.btn_export.clicked.connect(self.export_pdf)

        layout.addWidget(self.view)
        layout.addWidget(self.btn_export)
        self.setLayout(layout)

        self.render_html()

    def render_html(self):
        # Charger données depuis la base
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT objet, lieu, date_depart, duree, moyen_transport, financement FROM mission WHERE id=?", (self.mission_id,))
        mission = c.fetchone()

        c.execute("""SELECT nom, matricule, corps_grade, indice, fonction
                     FROM personnel p
                     JOIN mission_personnel mp ON mp.personnel_id = p.id
                     WHERE mp.mission_id=?""", (self.mission_id,))
        agents = [{
            "nom": row[0],
            "matricule": row[1],
            "grade": row[2],
            "indice": row[3],
            "fonction": row[4]
        } for row in c.fetchall()]
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

        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("ordre_mission.html")
        html_content = template.render(**data)

        # Sauvegarder temporairement pour affichage
        with open("preview_mission.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        self.view.load(QUrl.fromLocalFile(os.path.abspath("preview_mission.html")))

    def export_pdf(self):
        output, _ = QFileDialog.getSaveFileName(self, "Exporter en PDF", "ordre_de_mission.pdf", "PDF Files (*.pdf)")
        if output:
            self.view.page().printToPdf(output)
            QMessageBox.information(self, "Succès", f"PDF exporté : {output}")
