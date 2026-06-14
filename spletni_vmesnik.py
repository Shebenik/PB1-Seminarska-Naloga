# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import bottle
from bottle import route, run, template, request, redirect, static_file, TEMPLATE_PATH, response

# Pot do baze
DB_PATH = os.path.join(os.path.dirname(__file__), "prvaliga.db")

# Bottle bo iskal predloge v mapi views/
TEMPLATE_PATH.insert(0, os.path.join(os.path.dirname(__file__), "views"))
os.environ['BOTTLE_TEMPLATE_SUFFIX'] = '.html'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA encoding = 'UTF-8'")
    return conn


# ── DOMAČA STRAN ──────────────────────────────────────────────────────────────

@route("/")
def index():
    return redirect("/klubi")


# ── KLUBI ─────────────────────────────────────────────────────────────────────

@route("/klubi")
def klubi():
    sezona = request.query.get("sezona", "2025")
    try:
        sezona = int(sezona)
    except ValueError:
        sezona = 2025


    conn = get_conn()
    sezone = [r[0] for r in conn.execute(
        "SELECT DISTINCT sezona FROM statistika_klubov ORDER BY sezona DESC"
    ).fetchall()]

    lestvica = conn.execute("""
        SELECT k.id, k.ime, sk.pozicija, sk.zmage, sk.remi, sk.porazi,
               sk.dani_goli, sk.prejeti_goli,
               (sk.dani_goli - sk.prejeti_goli) AS razlika,
               sk.tocke
        FROM statistika_klubov sk
        JOIN klubi k ON k.id = sk.id_kluba
        WHERE sk.sezona = ?
        ORDER BY sk.pozicija
    """, (sezona,)).fetchall()
    conn.close()

    return template("klubi", lestvica=lestvica, sezone=sezone, sezona=sezona)


# ── KLUB – PROFIL ─────────────────────────────────────────────────────────────

@route("/klub/<id_kluba:int>")
def klub(id_kluba):
    sezona = request.query.get("sezona", "2025")
    try:
        sezona = int(sezona)
    except ValueError:
        sezona = 2025

    conn = get_conn()

    klub = conn.execute("SELECT * FROM klubi WHERE id = ?", (id_kluba,)).fetchone()
    if not klub:
        return template("napaka", sporocilo="Klub ne obstaja.")

    sezone = [r[0] for r in conn.execute(
        "SELECT DISTINCT sezona FROM statistika_klubov WHERE id_kluba = ? ORDER BY sezona DESC",
        (id_kluba,)
    ).fetchall()]

    statistika = conn.execute("""
        SELECT pozicija, zmage, remi, porazi, dani_goli, prejeti_goli,
               (dani_goli - prejeti_goli) AS razlika, tocke
        FROM statistika_klubov
        WHERE id_kluba = ? AND sezona = ?
    """, (id_kluba, sezona)).fetchone()

    igralci = conn.execute("""
        SELECT i.id, i.ime,
               si.goli, si.asistence, si.rumeni_kartoni, si.rdeci_kartoni,
               si.minute, si.nastopi
        FROM statistika_igralcev si
        JOIN igralci i ON i.id = si.id_igralca
        WHERE si.id_kluba = ? AND si.sezona = ?
        ORDER BY si.goli DESC, si.asistence DESC, i.ime
    """, (id_kluba, sezona)).fetchall()

    conn.close()
    return template("klub", klub=klub, statistika=statistika,
                    igralci=igralci, sezone=sezone, sezona=sezona)


# ── IGRALCI ───────────────────────────────────────────────────────────────────

@route("/igralci")
def igralci():
    sezona = request.query.get("sezona", "2025")
    try:
        sezona = int(sezona)
    except ValueError:
        sezona = 2025
    iskanje = request.query.get("q", "").encode('latin-1').decode('utf-8')
    iskanje = iskanje.strip()

    conn = get_conn()
    sezone = [r[0] for r in conn.execute(
        "SELECT DISTINCT sezona FROM statistika_igralcev ORDER BY sezona DESC"
    ).fetchall()]

    if iskanje:
        rezultati = conn.execute("""
            SELECT i.id, i.ime,
                   SUM(si.goli) AS goli, SUM(si.asistence) AS asistence,
                   SUM(si.nastopi) AS nastopi, SUM(si.minute) AS minute
            FROM igralci i
            JOIN statistika_igralcev si ON si.id_igralca = i.id
            WHERE i.ime LIKE ? AND si.sezona = ?
            GROUP BY i.id, i.ime
            ORDER BY goli DESC, asistence DESC, i.ime
        """, (f"%{iskanje}%", sezona)).fetchall()
    else:
        rezultati = conn.execute("""
            SELECT i.id, i.ime,
                   SUM(si.goli) AS goli, SUM(si.asistence) AS asistence,
                   SUM(si.nastopi) AS nastopi, SUM(si.minute) AS minute
            FROM igralci i
            JOIN statistika_igralcev si ON si.id_igralca = i.id
            WHERE si.sezona = ?
            GROUP BY i.id, i.ime
            ORDER BY goli DESC, asistence DESC, i.ime
        """, (sezona,)).fetchall()

    conn.close()
    return template("igralci", rezultati=rezultati, sezone=sezone,
                    sezona=sezona, iskanje=iskanje)


# ── IGRALEC – PROFIL ──────────────────────────────────────────────────────────

@route("/igralec/<id_igralca:int>")
def igralec(id_igralca):
    conn = get_conn()
    igralec = conn.execute("SELECT * FROM igralci WHERE id = ?", (id_igralca,)).fetchone()
    if not igralec:
        return template("napaka", sporocilo="Igralec ne obstaja.")

    kariera = conn.execute("""
        SELECT si.sezona, k.id AS id_kluba, k.ime AS klub,
               si.goli, si.asistence, si.rumeni_kartoni, si.rdeci_kartoni,
               si.minute, si.nastopi
        FROM statistika_igralcev si
        JOIN klubi k ON k.id = si.id_kluba
        WHERE si.id_igralca = ?
        ORDER BY si.sezona DESC, k.ime
    """, (id_igralca,)).fetchall()

    conn.close()
    return template("igralec", igralec=igralec, kariera=kariera)


# ── STRAN ZA NAPAKE ───────────────────────────────────────────────────────────

@route("/napaka")
def napaka():
    return template("napaka", sporocilo="Prišlo je do napake.")


# ── ZAGON ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
