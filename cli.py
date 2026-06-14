from repo import Repo

def meni():
    print("\n===== 1. SLOVENSKA NOGOMETNA LIGA – TEKSTOVNI VMESNIK =====")
    print("1) Prikaži vse igralce")
    print("2) Dodaj igralca")
    print("3) Prikaži vse klube")
    print("4) Dodaj klub")
    print("5) Prikaži statistiko igralca")
    print("6) Prikaži statistiko kluba")
    print("0) Izhod")
    print("===========================================================")

def izpis_igralcev(repo):
    print("\n--- IGRALCI ---")
    for r in repo.vsi_igralci():
        print(f"{r['id']}: {r['ime']}")

def dodaj_igralca(repo):
    ime = input("Vnesi ime igralca: ")
    repo.dodaj_igralca(ime)
    print("Igralec dodan.")

def izpis_klubov(repo):
    print("\n--- KLUBI ---")
    for r in repo.vsi_klubi():
        print(f"{r['id']}: {r['ime']}")

def dodaj_klub(repo):
    ime = input("Vnesi ime kluba: ")
    repo.dodaj_klub(ime)
    print("Klub dodan.")

def statistika_igralca(repo):
    try:
        id_igralca = int(input("ID igralca: "))
    except ValueError:
        print("ID mora biti število.")
        return

    podatki = repo.statistika_igralca(id_igralca)
    if not podatki:
        print("Ni podatkov.")
        return

    print("\n--- STATISTIKA IGRALCA ---")
    for r in podatki:
        print(dict(r))

def statistika_kluba(repo):
    try:
        id_kluba = int(input("ID kluba: "))
    except ValueError:
        print("ID mora biti število.")
        return

    podatki = repo.statistika_kluba(id_kluba)
    if not podatki:
        print("Ni podatkov.")
        return

    print("\n--- STATISTIKA KLUBA ---")
    for r in podatki:
        print(dict(r))

def main():
    repo = Repo()

    while True:
        meni()
        izbira = input("Izberi možnost: ")

        if izbira == "1":
            izpis_igralcev(repo)
        elif izbira == "2":
            dodaj_igralca(repo)
        elif izbira == "3":
            izpis_klubov(repo)
        elif izbira == "4":
            dodaj_klub(repo)
        elif izbira == "5":
            statistika_igralca(repo)
        elif izbira == "6":
            statistika_kluba(repo)
        elif izbira == "0":
            print("Izhod.")
            break
        else:
            print("Neveljavna izbira.")

if __name__ == "__main__":
    main()
