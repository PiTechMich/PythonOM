from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QDateEdit, QSpinBox, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import QDate, Qt
import sqlite3
from database import get_conn

class FenetreMission(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Créer / Modifier une mission")
        self.setMinimumWidth(400)
        self.mission_en_cours = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.objet = QLineEdit()
        self.lieu = QLineEdit()
        self.date_depart = QDateEdit()
        self.date_depart.setDate(QDate.currentDate())
        self.duree = QSpinBox()
        self.duree.setRange(1, 365)
        self.transport = QComboBox()
        self.transport.addItems(["Voiture administrative", "Taxi brousse", "Avion"])
        self.financement = QLineEdit()

        layout.addWidget(QLabel("Objet :"))
        layout.addWidget(self.objet)
        layout.addWidget(QLabel("Lieu :"))
        layout.addWidget(self.lieu)
        layout.addWidget(QLabel("Date de départ :"))
        layout.addWidget(self.date_depart)
        layout.addWidget(QLabel("Durée (jours) :"))
        layout.addWidget(self.duree)
        layout.addWidget(QLabel("Moyen de transport :"))
        layout.addWidget(self.transport)
        layout.addWidget(QLabel("Source de financement :"))
        layout.addWidget(self.financement)

        layout.addWidget(QLabel("Sélectionner les agents :"))
        self.liste_personnel = QListWidget()
        self.liste_personnel.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.liste_personnel)

        btn_save = QPushButton("Enregistrer mission")
        btn_save.clicked.connect(self.enregistrer_mission)
        layout.addWidget(btn_save)

        layout.addWidget(QLabel("Missions existantes :"))
        self.liste_missions = QListWidget()
        self.liste_missions.itemClicked.connect(self.charger_mission_selectionnee)
        layout.addWidget(self.liste_missions)

        btn_actions = QHBoxLayout()
        self.btn_modifier = QPushButton("Modifier mission")
        self.btn_modifier.clicked.connect(self.modifier_mission)
        self.btn_supprimer = QPushButton("Supprimer mission")
        self.btn_supprimer.clicked.connect(self.supprimer_mission)
        btn_actions.addWidget(self.btn_modifier)
        btn_actions.addWidget(self.btn_supprimer)
        layout.addLayout(btn_actions)

        self.setLayout(layout)
        self.load_personnel()
        self.load_missions()

    def load_personnel(self):
        self.liste_personnel.clear()
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nom FROM personnel ORDER BY nom")
        for id_, nom in c.fetchall():
            item = QListWidgetItem(nom)
            item.setData(Qt.UserRole, id_)
            self.liste_personnel.addItem(item)
        conn.close()

    def enregistrer_mission(self):
        objet = self.objet.text().strip()
        lieu = self.lieu.text().strip()
        date_depart = self.date_depart.date().toString("yyyy-MM-dd")
        duree = self.duree.value()
        transport = self.transport.currentText()
        financement = self.financement.text().strip()

        if not objet or not lieu or not financement:
            QMessageBox.warning(self, "Erreur", "Champs obligatoires manquants.")
            return

        selected_agents = self.liste_personnel.selectedItems()
        if not selected_agents:
            QMessageBox.warning(self, "Erreur", "Aucun agent sélectionné.")
            return

        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO mission (objet, lieu, date_depart, duree, moyen_transport, financement)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (objet, lieu, date_depart, duree, transport, financement))
        mission_id = c.lastrowid

        for item in selected_agents:
            c.execute("INSERT INTO mission_personnel (mission_id, personnel_id) VALUES (?, ?)",
                      (mission_id, item.data(Qt.UserRole)))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Succès", "Mission enregistrée.")
        self.load_missions()

    def load_missions(self):
        self.liste_missions.clear()
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, objet FROM mission ORDER BY id DESC")
        for id_, objet in c.fetchall():
            item = QListWidgetItem(f"Mission #{id_} - {objet}")
            item.setData(Qt.UserRole, id_)
            self.liste_missions.addItem(item)
        conn.close()

    def charger_mission_selectionnee(self, item):
        mission_id = item.data(Qt.UserRole)
        self.mission_en_cours = mission_id

        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT objet, lieu, date_depart, duree, moyen_transport, financement FROM mission WHERE id=?", (mission_id,))
        mission = c.fetchone()
        if not mission:
            return

        self.objet.setText(mission[0])
        self.lieu.setText(mission[1])
        self.date_depart.setDate(QDate.fromString(mission[2], "yyyy-MM-dd"))
        self.duree.setValue(mission[3])
        self.transport.setCurrentText(mission[4])
        self.financement.setText(mission[5])

        c.execute("SELECT personnel_id FROM mission_personnel WHERE mission_id=?", (mission_id,))
        agents_ids = {r[0] for r in c.fetchall()}

        for i in range(self.liste_personnel.count()):
            item = self.liste_personnel.item(i)
            item.setSelected(item.data(Qt.UserRole) in agents_ids)

        conn.close()

    def modifier_mission(self):
        if not self.mission_en_cours:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une mission à modifier.")
            return

        objet = self.objet.text().strip()
        lieu = self.lieu.text().strip()
        date_depart = self.date_depart.date().toString("yyyy-MM-dd")
        duree = self.duree.value()
        transport = self.transport.currentText()
        financement = self.financement.text().strip()

        if not objet or not lieu or not financement:
            QMessageBox.warning(self, "Erreur", "Champs obligatoires manquants.")
            return

        selected_agents = self.liste_personnel.selectedItems()
        if not selected_agents:
            QMessageBox.warning(self, "Erreur", "Aucun agent sélectionné.")
            return

        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            UPDATE mission SET objet=?, lieu=?, date_depart=?, duree=?, moyen_transport=?, financement=?
            WHERE id=?
        """, (objet, lieu, date_depart, duree, transport, financement, self.mission_en_cours))

        c.execute("DELETE FROM mission_personnel WHERE mission_id=?", (self.mission_en_cours,))
        for item in selected_agents:
            c.execute("INSERT INTO mission_personnel (mission_id, personnel_id) VALUES (?, ?)",
                      (self.mission_en_cours, item.data(Qt.UserRole)))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Succès", "Mission modifiée.")
        self.load_missions()

    def supprimer_mission(self):
        if not self.mission_en_cours:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une mission à supprimer.")
            return

        reponse = QMessageBox.question(self, "Confirmation", "Supprimer cette mission ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if reponse == QMessageBox.Yes:
            conn = get_conn()
            c = conn.cursor()
            c.execute("DELETE FROM mission_personnel WHERE mission_id=?", (self.mission_en_cours,))
            c.execute("DELETE FROM mission WHERE id=?", (self.mission_en_cours,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Mission supprimée.")
            self.load_missions()
            self.objet.clear()
            self.lieu.clear()
            self.financement.clear()
            self.liste_personnel.clearSelection()
            self.mission_en_cours = None
