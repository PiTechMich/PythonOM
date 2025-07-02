import sqlite3

DB_NAME = "ordre_mission.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            matricule TEXT UNIQUE NOT NULL,
            corps_grade TEXT,
            indice INTEGER,
            fonction TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS mission (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objet TEXT NOT NULL,
            lieu TEXT NOT NULL,
            date_depart TEXT NOT NULL,
            duree INTEGER,
            moyen_transport TEXT,
            financement TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS mission_personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER,
            personnel_id INTEGER,
            FOREIGN KEY (mission_id) REFERENCES mission(id),
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_NAME)
