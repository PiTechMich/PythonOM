from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt  # ✅ Ajout obligatoire

import sqlite3
from database import get_conn
class FenetrePersonnel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Personnel")
        self.resize(700, 400)
        self.init_ui()
        self.load_personnel()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulaire
        form_layout = QHBoxLayout()

        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom")
        form_layout.addWidget(self.nom)

        self.matricule = QLineEdit()
        self.matricule.setPlaceholderText("Matricule")
        form_layout.addWidget(self.matricule)

        self.corps_grade = QLineEdit()
        self.corps_grade.setPlaceholderText("Corps/Grade")
        form_layout.addWidget(self.corps_grade)

        self.indice = QLineEdit()
        self.indice.setPlaceholderText("Indice")
        form_layout.addWidget(self.indice)

        self.fonction = QLineEdit()
        self.fonction.setPlaceholderText("Fonction")
        form_layout.addWidget(self.fonction)

        layout.addLayout(form_layout)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_modifier = QPushButton("Modifier")
        self.btn_supprimer = QPushButton("Supprimer")

        self.btn_ajouter.clicked.connect(self.ajouter_personnel)
        self.btn_modifier.clicked.connect(self.modifier_personnel)
        self.btn_supprimer.clicked.connect(self.supprimer_personnel)

        btn_layout.addWidget(self.btn_ajouter)
        btn_layout.addWidget(self.btn_modifier)
        btn_layout.addWidget(self.btn_supprimer)

        layout.addLayout(btn_layout)

        # Table affichage
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nom", "Matricule", "Corps/Grade", "Indice", "Fonction"]
        )
        self.table.cellClicked.connect(self.remplir_formulaire)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_personnel(self):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM personnel ORDER BY nom")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                if col_idx == 0:
                    item.setFlags(item.flags() & ~ (Qt.ItemIsEditable))
                self.table.setItem(row_idx, col_idx, item)

        self.clear_formulaire()

    def clear_formulaire(self):
        self.nom.clear()
        self.matricule.clear()
        self.corps_grade.clear()
        self.indice.clear()
        self.fonction.clear()
        self.table.clearSelection()

    def remplir_formulaire(self, row, _):
        self.nom.setText(self.table.item(row, 1).text())
        self.matricule.setText(self.table.item(row, 2).text())
        self.corps_grade.setText(self.table.item(row, 3).text())
        self.indice.setText(self.table.item(row, 4).text())
        self.fonction.setText(self.table.item(row, 5).text())

    def ajouter_personnel(self):
        nom = self.nom.text().strip()
        matricule = self.matricule.text().strip()
        corps = self.corps_grade.text().strip()
        indice = self.indice.text().strip()
        fonction = self.fonction.text().strip()

        if not nom or not matricule:
            QMessageBox.warning(self, "Erreur", "Nom et Matricule sont obligatoires")
            return

        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                INSERT INTO personnel (nom, matricule, corps_grade, indice, fonction)
                VALUES (?, ?, ?, ?, ?)
            """, (nom, matricule, corps, indice if indice.isdigit() else None, fonction))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Agent ajouté")
            self.load_personnel()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Erreur", "Matricule déjà utilisé")

    def modifier_personnel(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à modifier")
            return
        personnel_id = int(self.table.item(selected, 0).text())

        nom = self.nom.text().strip()
        matricule = self.matricule.text().strip()
        corps = self.corps_grade.text().strip()
        indice = self.indice.text().strip()
        fonction = self.fonction.text().strip()

        if not nom or not matricule:
            QMessageBox.warning(self, "Erreur", "Nom et Matricule sont obligatoires")
            return

        try:
            conn = get_conn()
            c = conn.cursor()
            c.execute("""
                UPDATE personnel SET nom=?, matricule=?, corps_grade=?, indice=?, fonction=?
                WHERE id=?
            """, (nom, matricule, corps, indice if indice.isdigit() else None, fonction, personnel_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Agent modifié")
            self.load_personnel()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Erreur", "Matricule déjà utilisé")

    def supprimer_personnel(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une ligne à supprimer")
            return
        personnel_id = int(self.table.item(selected, 0).text())
        confirm = QMessageBox.question(self, "Confirmer suppression",
                                       "Supprimer cet agent ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = get_conn()
            c = conn.cursor()
            c.execute("DELETE FROM personnel WHERE id=?", (personnel_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Agent supprimé")
            self.load_personnel()
