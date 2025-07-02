import os

# ✅ Forcer OpenGL logiciel (évite les erreurs libGL)
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PyQt5.QtCore import QCoreApplication, Qt
# ✅ Nécessaire pour QtWebEngine
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QInputDialog

from personnel_ui import FenetrePersonnel
from mission_ui import FenetreMission
from database import init_db

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Ordres de Mission")
        self.resize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        btn_personnel = QPushButton("Gérer le Personnel")
        btn_personnel.clicked.connect(self.ouvrir_fenetre_personnel)
        layout.addWidget(btn_personnel)

        btn_mission = QPushButton("Nouvelle Mission")
        btn_mission.clicked.connect(self.ouvrir_fenetre_mission)
        layout.addWidget(btn_mission)

        btn_imprimer = QPushButton("Imprimer mission")
        btn_imprimer.clicked.connect(self.imprimer_mission)
        layout.addWidget(btn_imprimer)

        self.setLayout(layout)

        self.fenetre_personnel = None
        self.fenetre_mission = None

    def ouvrir_fenetre_personnel(self):
        if self.fenetre_personnel is None or not self.fenetre_personnel.isVisible():
            self.fenetre_personnel = FenetrePersonnel()
            self.fenetre_personnel.show()
        else:
            self.fenetre_personnel.raise_()
            self.fenetre_personnel.activateWindow()

    def ouvrir_fenetre_mission(self):
        if self.fenetre_mission is None or not self.fenetre_mission.isVisible():
            self.fenetre_mission = FenetreMission()
            self.fenetre_mission.show()
        else:
            self.fenetre_mission.raise_()
            self.fenetre_mission.activateWindow()

    def imprimer_mission(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        from print_mission import generer_pdf_reportlab

        mission_id, ok = QInputDialog.getInt(self, "ID Mission", "Entrez l'ID de la mission :")
        if ok:
            try:
                generer_pdf_reportlab(mission_id)
                QMessageBox.information(self, "Succès", "PDF généré avec succès !")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération : {e}")

def main():
    init_db()
    app = QApplication([])
    main_win = MainApp()
    main_win.show()
    app.exec_()

if __name__ == "__main__":
    main()
