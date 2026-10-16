
# ============================================================
# GAME SALES ANALYTICS
# MODUL: DATA LOADER
# ============================================================
#
# Aufgabe:
#   Daten aus unserer SQLite-Datenbank laden.
#
# Vorteil:
#   Alle Dashboard-Seiten können später
#   dieselbe Funktion verwenden.
#
# ============================================================


# Bibliotheken importieren.

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# 1. DATENBANKPFAD DEFINIEREN
# ============================================================

# Diese Datei liegt im Ordner dashboard/.
#
# parent.parent:
#   Ermittelt den Projekt-Hauptordner.

BASE_DIR = Path(__file__).resolve().parent.parent

# Pfad zur SQLite-Datenbank.

DATABASE_PATH = BASE_DIR / "database" / "games.db"


# ============================================================
# 2. DATEN AUS SQLITE LADEN
# ============================================================

# Der Decorator speichert die geladenen Daten
# vorübergehend im Streamlit-Cache.
#
# ttl=300:
#   Cache-Gültigkeit bis zu fünf Minuten.

@st.cache_data(ttl=300)
def load_data():

    # Überprüfen, ob die Datenbank existiert.

    if not DATABASE_PATH.is_file():

        raise FileNotFoundError(
            f"Datenbank nicht gefunden: {DATABASE_PATH}"
        )

    # Datenbankverbindung öffnen.

    connection = sqlite3.connect(DATABASE_PATH)

    try:

        # Alle Spiele aus der Datenbank laden.

        query = """
        SELECT *
        FROM games;
        """

        # SQL-Ergebnis als Pandas-Tabelle speichern.

        df = pd.read_sql_query(
            query,
            connection
        )

    finally:

        # Verbindung zuverlässig schließen.

        connection.close()

    # DataFrame an die aufrufende Datei zurückgeben.

    return df
