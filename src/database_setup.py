
# ============================================================
# GAME SALES ANALYTICS
# MODUL: DATABASE SETUP
# ============================================================
#
# Ziel:
#   Eine SQLite-Datenbank erstellen und unsere
#   bereinigten Videospieldaten darin speichern.
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# sqlite3:
#   Gehört zur Python-Standardbibliothek.
#
#   Damit können wir SQLite-Datenbanken erstellen,
#   SQL-Abfragen ausführen und Daten speichern.

import sqlite3

# Pandas:
#   Damit lesen wir unsere bereinigte CSV-Datei ein.

import pandas as pd

# Path:
#   Hilft beim Arbeiten mit Dateipfaden.

from pathlib import Path


# ============================================================
# 2. DATEIPFADE FESTLEGEN
# ============================================================

# Projekt-Hauptordner bestimmen.
#
# database_setup.py befindet sich in "src".
# Deshalb gehen wir zwei Ebenen nach oben.

BASE_DIR = Path(__file__).resolve().parent.parent


# Pfad unserer bereinigten CSV-Datei.

CSV_PATH = (
    BASE_DIR / "data" / "processed" / "vgsales_clean.csv"
)


# Speicherort unserer SQLite-Datenbank.
#
# Die Datenbank wird als Datei games.db gespeichert.

DATABASE_PATH = BASE_DIR / "database" / "games.db"


# Ordner erstellen, falls er nicht existiert.

DATABASE_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. BEREINIGTE DATEN LADEN
# ============================================================

print("\n=== DATENBANK-EINRICHTUNG ===")


# CSV-Datei in einen Pandas-DataFrame laden.

df = pd.read_csv(CSV_PATH)


# Anzahl der geladenen Spiele ausgeben.

print("Geladene Spiele:", len(df))


# ============================================================
# 4. VERBINDUNG ZUR DATENBANK HERSTELLEN
# ============================================================

# connect():
#   Öffnet eine Verbindung zu unserer SQLite-Datenbank.
#
# Wenn games.db noch nicht existiert,
# erstellt SQLite die Datei automatisch.
#
# Die Verbindung speichern wir in "connection".

connection = sqlite3.connect(DATABASE_PATH)


# ============================================================
# 5. DATEN IN SQLITE SPEICHERN
# ============================================================

# to_sql():
#   Überträgt unseren Pandas-DataFrame
#   in eine SQL-Datenbanktabelle.
#
# name="games":
#   Die Tabelle erhält den Namen "games".
#
# con=connection:
#   Gibt die Datenbankverbindung an.
#
# if_exists="replace":
#   Falls die Tabelle bereits existiert,
#   wird sie gelöscht und neu erstellt.
#
#   ACHTUNG:
#   Dabei werden bisherige Inhalte dieser
#   Tabelle überschrieben!
#
# index=False:
#   Verhindert, dass zusätzliche Pandas-
#   Zeilennummern gespeichert werden.

df.to_sql(
    name="games",
    con=connection,
    if_exists="replace",
    index=False
)


# ============================================================
# 6. DATENBANK ÜBERPRÜFEN
# ============================================================

# SQL-Abfrage:
#
# SELECT COUNT(*)
#   Zählt alle Zeilen einer Tabelle.
#
# FROM games
#   Legt fest, aus welcher Tabelle
#   die Daten gelesen werden sollen.

query = "SELECT COUNT(*) FROM games"


# read_sql_query():
#   Führt eine SQL-Abfrage aus und
#   speichert das Ergebnis als DataFrame.

result = pd.read_sql_query(
    query,
    connection
)


print("\n=== SPIELE IN DER DATENBANK ===")

print(result)


# ============================================================
# 7. DATENBANKVERBINDUNG SCHLIESSEN
# ============================================================

# close():
#   Schließt unsere Datenbankverbindung.
#
# Das ist wichtig, damit verwendete
# Ressourcen wieder freigegeben werden.

connection.close()


# ============================================================
# 8. PROGRAMMENDE
# ============================================================

print("\nDatenbank erfolgreich erstellt!")

print("Speicherort:", DATABASE_PATH)
