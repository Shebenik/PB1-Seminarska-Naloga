import sqlite3
import os

class Repo:
    def __init__(self, path=None):
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prvaliga.db")
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA encoding = 'UTF-8'")

    # ---------------- SEZONE ----------------

    def sezone_klubov(self):
        return [r[0] for r in self.conn.execute(
            "SELECT DISTINCT sezona FROM statistika_klubov ORDER BY sezona DESC"
        ).fetchall()]

    def sezone_kluba(self, id_kluba):
        return [r[0] for r in self.conn.execute(
            "SELECT DISTINCT sezona FROM statistika_klubov WHERE id_kluba = ? ORDER BY sezona DESC",
            (id_kluba,)
        ).fetchall()]

    def sezone_igralcev(self):
        return [r[0] for r in self.conn.execute(
            "SELECT DISTINCT sezona FROM statistika_igralcev ORDER BY sezona DESC"
        ).fetchall()]

    # ---------------- KLUBI ----------------

    def vsi_klubi(self):
        return self.conn.execute("SELECT * FROM klubi").fetchall()

    def dodaj_klub(self, ime):
        self.conn.execute("INSERT INTO klubi (ime) VALUES (?)", (ime,))
        self.conn.commit()

    def lestvica(self, sezona):
        return self.conn.execute("""
            SELECT k.id, k.ime, sk.pozicija, sk.zmage, sk.remi, sk.porazi,
                   sk.dani_goli, sk.prejeti_goli,
                   (sk.dani_goli - sk.prejeti_goli) AS razlika,
                   sk.tocke
            FROM statistika_klubov sk
            JOIN klubi k ON k.id = sk.id_kluba
            WHERE sk.sezona = ?
            ORDER BY sk.pozicija
        """, (sezona,)).fetchall()

    def klub(self, id_kluba):
        return self.conn.execute(
            "SELECT * FROM klubi WHERE id = ?", (id_kluba,)
        ).fetchone()

    def statistika_kluba(self, id_kluba, sezona=None):
        if sezona is None:
            return self.conn.execute("""
                SELECT * FROM statistika_klubov
                WHERE id_kluba = ?
            """, (id_kluba,)).fetchall()
        return self.conn.execute("""
            SELECT pozicija, zmage, remi, porazi, dani_goli, prejeti_goli,
                   (dani_goli - prejeti_goli) AS razlika, tocke
            FROM statistika_klubov
            WHERE id_kluba = ? AND sezona = ?
        """, (id_kluba, sezona)).fetchone()

    def igralci_kluba(self, id_kluba, sezona):
        return self.conn.execute("""
            SELECT i.id, i.ime,
                   si.goli, si.asistence, si.rumeni_kartoni, si.rdeci_kartoni,
                   si.minute, si.nastopi
            FROM statistika_igralcev si
            JOIN igralci i ON i.id = si.id_igralca
            WHERE si.id_kluba = ? AND si.sezona = ?
            ORDER BY si.goli DESC, si.asistence DESC, i.ime
        """, (id_kluba, sezona)).fetchall()

    # ---------------- IGRALCI ----------------

    def vsi_igralci(self):
        return self.conn.execute("SELECT * FROM igralci").fetchall()

    def dodaj_igralca(self, ime):
        self.conn.execute("INSERT INTO igralci (ime) VALUES (?)", (ime,))
        self.conn.commit()

    def seznam_igralcev(self, sezona, iskanje=None):
        if iskanje:
            return self.conn.execute("""
                SELECT i.id, i.ime,
                       SUM(si.goli) AS goli, SUM(si.asistence) AS asistence,
                       SUM(si.nastopi) AS nastopi, SUM(si.minute) AS minute
                FROM igralci i
                JOIN statistika_igralcev si ON si.id_igralca = i.id
                WHERE i.ime LIKE ? AND si.sezona = ?
                GROUP BY i.id, i.ime
                ORDER BY goli DESC, asistence DESC, i.ime
            """, (f"%{iskanje}%", sezona)).fetchall()
        return self.conn.execute("""
            SELECT i.id, i.ime,
                   SUM(si.goli) AS goli, SUM(si.asistence) AS asistence,
                   SUM(si.nastopi) AS nastopi, SUM(si.minute) AS minute
            FROM igralci i
            JOIN statistika_igralcev si ON si.id_igralca = i.id
            WHERE si.sezona = ?
            GROUP BY i.id, i.ime
            ORDER BY goli DESC, asistence DESC, i.ime
        """, (sezona,)).fetchall()

    def statistika_igralca(self, id_igralca):
        return self.conn.execute("""
            SELECT * FROM statistika_igralcev
            WHERE id_igralca = ?
        """, (id_igralca,)).fetchall()

    def igralec(self, id_igralca):
        return self.conn.execute(
            "SELECT * FROM igralci WHERE id = ?", (id_igralca,)
        ).fetchone()

    def kariera_igralca(self, id_igralca):
        return self.conn.execute("""
            SELECT si.sezona, k.id AS id_kluba, k.ime AS klub,
                   si.goli, si.asistence, si.rumeni_kartoni, si.rdeci_kartoni,
                   si.minute, si.nastopi
            FROM statistika_igralcev si
            JOIN klubi k ON k.id = si.id_kluba
            WHERE si.id_igralca = ?
            ORDER BY si.sezona DESC, k.ime
        """, (id_igralca,)).fetchall()
