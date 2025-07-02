from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import sqlite3

class AjouterPersonnel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ajouter un agent")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom")
        layout.addWidget(QLabel("Nom :"))
        layout.addWidget(self.nom)

        self.matricule = QLineEdit()
        self.matricule.setPlaceholderText("Matricule")
        layout.addWidget(QLabel("Matricule :"))
        layout.addWidget(self.matricule)

        self.corps_grade = QLineEdit()
        self.corps_grade.setPlaceholderText("Corps/Grade")
        layout.addWidget(QLabel("Corps/Grade :"))
        layout.addWidget(self.corps_grade)

        self.indice = QLineEdit()
        self.indice.setPlaceholderText("Indice")
        layout.addWidget(QLabel("Indice :"))
        layout.addWidget(self.indice)

        self.fonction = QLineEdit()
        self.fonction.setPlaceholderText("Fonction")
        layout.addWidget(QLabel("Fonction :"))
        layout.addWidget(self.fonction)

        bouton = QPushButton("Enregistrer")
        bouton.clicked.connect(self.enregistrer_personnel)
        layout.addWidget(bouton)

        self.setLayout(layout)

    def enregistrer_personnel(self):
        nom = self.nom.text()
        matricule = self.matricule.text()
        corps = self.corps_grade.text()
        indice = self.indice.text()
        fonction = self.fonction.text()

        if not nom or not matricule:
            QMessageBox.warning(self, "Erreur", "Nom et Matricule sont obligatoires.")
            return

        try:
            conn = sqlite3.connect("ordre_mission.db")
            c = conn.cursor()
            c.execute('''
                INSERT INTO personnel (nom, matricule, corps_grade, indice, fonction)
                VALUES (?, ?, ?, ?, ?)
            ''', (nom, matricule, corps, indice, fonction))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Agent enregistré avec succès.")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Erreur", "Matricule déjà utilisé.")
