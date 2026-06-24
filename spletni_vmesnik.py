# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import bottle
from bottle import route, run, template, request, redirect, TEMPLATE_PATH
from repo import Repo

# Bottle bo iskal predloge v mapi views/
TEMPLATE_PATH.insert(0, os.path.join(os.path.dirname(__file__), "views"))
os.environ['BOTTLE_TEMPLATE_SUFFIX'] = '.html'

repo = Repo()


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

    sezone = repo.sezone_klubov()
    lestvica = repo.lestvica(sezona)

    return template("klubi", lestvica=lestvica, sezone=sezone, sezona=sezona)


# ── KLUB – PROFIL ─────────────────────────────────────────────────────────────

@route("/klub/<id_kluba:int>")
def klub(id_kluba):
    sezona = request.query.get("sezona", "2025")
    try:
        sezona = int(sezona)
    except ValueError:
        sezona = 2025

    klub = repo.klub(id_kluba)
    if not klub:
        return template("napaka", sporocilo="Klub ne obstaja.")

    sezone = repo.sezone_kluba(id_kluba)
    statistika = repo.statistika_kluba(id_kluba, sezona)
    igralci = repo.igralci_kluba(id_kluba, sezona)

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

    sezone = repo.sezone_igralcev()
    rezultati = repo.seznam_igralcev(sezona, iskanje or None)

    return template("igralci", rezultati=rezultati, sezone=sezone,
                    sezona=sezona, iskanje=iskanje)


# ── IGRALEC – PROFIL ──────────────────────────────────────────────────────────

@route("/igralec/<id_igralca:int>")
def igralec(id_igralca):
    igralec = repo.igralec(id_igralca)
    if not igralec:
        return template("napaka", sporocilo="Igralec ne obstaja.")

    kariera = repo.kariera_igralca(id_igralca)

    return template("igralec", igralec=igralec, kariera=kariera)


# ── STRAN ZA NAPAKE ───────────────────────────────────────────────────────────

@route("/napaka")
def napaka():
    return template("napaka", sporocilo="Prišlo je do napake.")


# ── ZAGON ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True, reloader=True)
