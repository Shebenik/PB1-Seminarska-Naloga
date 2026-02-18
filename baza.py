import sqlite3
import csv
import os

# CSV mapa
csv_dir = "csv_exports"

# CSV datoteke
clubs_csv = os.path.join(csv_dir, "klubi.csv")
players_csv = os.path.join(csv_dir, "igralci.csv")
player_stats_csv = os.path.join(csv_dir, "statistika_igralcev.csv")
club_stats_csv = os.path.join(csv_dir, "statistika_klubov.csv")

# Bazna datoteka
db_file = "prvaliga7.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
CREATE TABLE klubi (
    id INTEGER PRIMARY KEY, 
    ime TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE igralci (
    id INTEGER PRIMARY KEY, 
    ime TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE statistika_igralcev (
    id_igralca INTEGER NOT NULL,
    id_kluba INTEGER NOT NULL,
    sezona INTEGER NOT NULL,
    goli INTEGER DEFAULT 0,
    asistence INTEGER DEFAULT 0,
    rumeni_kartoni INTEGER DEFAULT 0,
    rdeci_kartoni INTEGER DEFAULT 0,
    minute INTEGER DEFAULT 0,
    nastopi INTEGER DEFAULT 0,
    FOREIGN KEY (id_igralca) REFERENCES igralci(id),
    FOREIGN KEY (id_kluba) REFERENCES klubi(id),
    PRIMARY KEY (id_igralca, id_kluba, sezona)
)
""")

cursor.execute("""
CREATE TABLE statistika_klubov (
    id_kluba INTEGER NOT NULL,
    sezona INTEGER NOT NULL,
    pozicija INTEGER DEFAULT 0,
    zmage INTEGER DEFAULT 0,
    remi INTEGER DEFAULT 0,
    porazi INTEGER DEFAULT 0,
    dani_goli INTEGER DEFAULT 0,
    prejeti_goli INTEGER DEFAULT 0,
    tocke INTEGER DEFAULT 0,
    FOREIGN KEY (id_kluba) REFERENCES klubi(id),
    PRIMARY KEY (id_kluba, sezona)
)
""")

conn.commit()

# Uvozimo klube
with open(clubs_csv, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # preskočimo naslove podatkov
    clubs_import = list(reader)
    cursor.executemany("INSERT OR IGNORE INTO klubi (id, ime) VALUES (?, ?)", clubs_import)
conn.commit()

# Uvozimo igralce
with open(players_csv, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # preskočimo naslove podatkov
    players_import = list(reader)
    cursor.executemany("INSERT OR IGNORE INTO igralci (id, ime) VALUES (?, ?)", players_import)
conn.commit()

# Uvozimo statistiko klubov
with open(club_stats_csv, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # preskočimo naslove podatkov
    club_stats_import = list(reader)
    cursor.executemany("""
        INSERT OR REPLACE INTO statistika_klubov 
        (id_kluba, sezona, pozicija, zmage, remi, porazi, dani_goli, prejeti_goli, tocke) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, club_stats_import)
conn.commit()

# Uvozimo statistiko igralcev
with open(player_stats_csv, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)  # preskočimo naslove podatkov
    player_stats_import = list(reader)
    cursor.executemany("""
        INSERT OR REPLACE INTO statistika_igralcev
        (id_igralca, id_kluba, sezona, goli, asistence, rumeni_kartoni, rdeci_kartoni, minute, nastopi) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, player_stats_import)
conn.commit()

conn.close()