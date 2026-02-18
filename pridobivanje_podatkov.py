import requests
from bs4 import BeautifulSoup
import re
import csv
import os

# Seasons
seasons = [2025, 2024, 2023, 2022, 2021]

# Base URLs
leaderboard_url = "https://www.prvaliga.si/tekmovanja/default.asp"
player_url = "https://www.prvaliga.si/tekmovanja/default.asp"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# Ustvarimo mapo v kateri bodo podatki
csv_dir = "csv_exports"
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)

# Ustvarimo poti csv datotek
clubs_csv = os.path.join(csv_dir, "klubi.csv")
players_csv = os.path.join(csv_dir, "igralci.csv")
player_stats_csv = os.path.join(csv_dir, "statistika_igralcev.csv")
club_stats_csv = os.path.join(csv_dir, "statistika_klubov.csv")

# Zberemo podatke iz lestvice
clubs_data = []
club_stats_data = []

for season in seasons: 
    params = {"action": "lestvica", "id_menu": "102", "id_sezone": season}
    response = requests.get(leaderboard_url, params=params, headers=headers, timeout=10)
    response.encoding = "utf-8"
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Najdemo del kode v katerem je zapisana lestvica
    table = soup.find("table", class_=re.compile(r"Tabela1", re.I))
    if not table:
        table = soup.find("table", class_=re.compile(r"table", re.I))
    if table:
        rows = table.find_all("tr", class_="hand")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 11:
                continue
            onclick = row.get("onclick", "")
            match = re.search(r"id_kluba=(\d+)", onclick)
            if not match:
                continue
            klub_id = int(match.group(1))
            klub_name = tds[3].get_text(strip=True)
            
            # Dodamo v seznam klubov, da se izognemo duplikatov
            if not any(c[0] == klub_id for c in clubs_data):
                clubs_data.append([klub_id, klub_name])

            # Statistika ekipe - DODANO mesto (position)
            try:
                position = tds[0].get_text(strip=True).replace('.', '')  # Odstranimo piko
                position = int(position) if position else 0
                
                wins = int(tds[5].get_text(strip=True) or 0)
                draws = int(tds[6].get_text(strip=True) or 0)
                losses = int(tds[7].get_text(strip=True) or 0)
                
                goals_text = tds[8].get_text(strip=True)
                if ":" in goals_text:
                    goals_for, goals_against = map(int, goals_text.split(":"))
                else:
                    goals_for, goals_against = 0, 0
                    
                points = int(tds[10].get_text(strip=True) or 0)

                club_stats_data.append([
                    klub_id, season, position, wins, draws, losses, 
                    goals_for, goals_against, points
                ])
                
            except (ValueError, IndexError) as e:
                print(f"    Error parsing team stats for {klub_name}: {e}")
                continue
        
# Zapišemo klube v CSV datoteko
with open(clubs_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'ime'])  # Imena podatkov
    writer.writerows(clubs_data)
    
# Zapišemo statistiko klubov v CSV datoteko - DODANO mesto
with open(club_stats_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id_kluba', 'sezona', 'pozicija', 'zmage', 'remi', 'porazi', 
                     'dani_goli', 'prejeti_goli', 'tocke'])  # Imena podatkov
    writer.writerows(club_stats_data)

# Zberemo podatke igralcev posameznega kluba
players_data = []
player_stats_data = []
# Ustvarimo množico, da ne pride do ponovitev istih igralcev
unique_players = set()

for season in seasons:
    for klub_id, klub_name in clubs_data:
        params = {"action": "klub", "id_menu": "217", "id_kluba": klub_id, "prikaz": "5", "id_sezone": season}
        response = requests.get(player_url, params=params, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr", class_="hand")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 8:
                continue
            onclick = row.get("onclick", "")
            match = re.search(r"id_igralca=(\d+)", onclick)
            if not match:
                continue
            igralec_id = int(match.group(1))
            player_name = tds[1].get_text(separator=" ", strip=True).replace("\xa0", " ")
            # Dodamo igralčeve podatke v seznam igralcev
            if igralec_id not in unique_players:
                unique_players.add(igralec_id)
                players_data.append([igralec_id, player_name])
            try:
                goals = int(tds[2].get_text(strip=True) or 0)
                assists = int(tds[3].get_text(strip=True) or 0)
                yellow = int(tds[4].get_text(strip=True) or 0)
                red = int(tds[5].get_text(strip=True) or 0)
                minutes = int(tds[6].get_text(strip=True) or 0)
                appearances = int(tds[7].get_text(strip=True) or 0)
            except ValueError:
                goals = assists = yellow = red = minutes = appearances = 0
            player_stats_data.append([
                igralec_id, klub_id, season, goals, assists, 
                yellow, red, minutes, appearances
            ])
# Zapišemo igralce v CSV datoteko
with open(players_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'ime'])  # Imena podatkov
    writer.writerows(players_data)

# Zapišemo statistiko igralcev v CSV datoteko
with open(player_stats_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id_igralca', 'id_kluba', 'sezona', 'goli', 'asistence', 
                     'rumeni_kartoni', 'rdeci_kartoni', 'minute', 'nastopi'])  # Imena podatkov
    writer.writerows(player_stats_data)