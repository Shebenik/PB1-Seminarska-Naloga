import sqlite3

class Repo:
    def __init__(self, path="prvaliga.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

    # ---------------- IGRALCI ----------------
    def vsi_igralci(self):
        return self.conn.execute("SELECT * FROM igralci").fetchall()

    def dodaj_igralca(self, ime):
        self.conn.execute("INSERT INTO igralci (ime) VALUES (?)", (ime,))
        self.conn.commit()

    # ---------------- KLUBI ----------------
    def vsi_klubi(self):
        return self.conn.execute("SELECT * FROM klubi").fetchall()

    def dodaj_klub(self, ime):
        self.conn.execute("INSERT INTO klubi (ime) VALUES (?)", (ime,))
        self.conn.commit()

    # ---------------- STATISTIKA IGRALCEV ----------------
    def statistika_igralca(self, id_igralca):
        return self.conn.execute("""
            SELECT * FROM statistika_igralcev
            WHERE id_igralca = ?
        """, (id_igralca,)).fetchall()

    # ---------------- STATISTIKA KLUBOV ----------------
    def statistika_kluba(self, id_kluba):
        return self.conn.execute("""
            SELECT * FROM statistika_klubov
            WHERE id_kluba = ?
        """, (id_kluba,)).fetchall()
