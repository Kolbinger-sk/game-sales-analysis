
# ============================================================
# GAME SALES ANALYTICS
# MODUL: SQL ANALYSIS
# ============================================================
#
# Projekt:
#   Analyse weltweiter Videospiel-Verkaufszahlen
#
# Aufgabe dieses Moduls:
#   Daten aus unserer SQLite-Datenbank auslesen,
#   filtern, gruppieren und statistisch analysieren.
#
# Verwendete Bibliotheken:
#   - sqlite3: Verbindung zur SQLite-Datenbank
#   - pandas: Darstellung der SQL-Ergebnisse
#   - pathlib: Verwaltung der Dateipfade
#
# Folgende SQL-Funktionen lernen wir:
#   1. SELECT
#   2. FROM
#   3. WHERE
#   4. ORDER BY
#   5. LIMIT
#   6. COUNT()
#   7. SUM()
#   8. GROUP BY
#   9. AVG()
#   10. HAVING
#   11. AND
#   12. ROUND()
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# sqlite3:
#   Gehört zur Python-Standardbibliothek.
#
#   Ermöglicht das Verbinden mit SQLite-Datenbanken
#   und das Ausführen von SQL-Abfragen.

import sqlite3


# pandas:
#   Ermöglicht uns, die Ergebnisse unserer
#   SQL-Abfragen als Tabellen darzustellen.
#
#   "pd" ist der übliche Alias für pandas.

import pandas as pd


# pathlib:
#   Stellt die Klasse Path bereit.
#
#   Damit können wir Dateipfade unabhängig
#   vom verwendeten Betriebssystem erstellen.

from pathlib import Path


# ============================================================
# 2. PROJEKTPFADE DEFINIEREN
# ============================================================

# __file__:
#   Enthält den Dateipfad der aktuellen Python-Datei.
#
# resolve():
#   Wandelt den Pfad in einen absoluten Pfad um.
#
# parent:
#   Gibt den übergeordneten Ordner zurück.
#
# parent.parent:
#   Geht zwei Verzeichnisebenen nach oben.
#
# Da sql_analysis.py im Ordner src liegt,
# gelangen wir so zum Hauptordner unseres Projekts.

BASE_DIR = Path(__file__).resolve().parent.parent


# DATABASE_PATH:
#   Speichert den vollständigen Pfad zu unserer
#   SQLite-Datenbank games.db.
#
# Die Datenbank liegt im Unterordner database/.

DATABASE_PATH = BASE_DIR / "database" / "games.db"


# ============================================================
# 3. DATENBANKDATEI ÜBERPRÜFEN
# ============================================================

# exists():
#   Prüft, ob eine Datei oder ein Ordner existiert.
#
# Wenn die Datenbank nicht gefunden wird,
# geben wir eine verständliche Fehlermeldung aus.
#
# Das ist wichtig, weil sqlite3.connect()
# sonst unter Umständen eine neue leere
# Datenbank erstellen würde.

if not DATABASE_PATH.is_file():

    raise FileNotFoundError(
        f"Die Datenbank wurde nicht gefunden: {DATABASE_PATH}"
    )


# ============================================================
# 4. DATENBANKVERBINDUNG HERSTELLEN
# ============================================================

# sqlite3.connect():
#   Öffnet eine Verbindung zu unserer Datenbank.
#
# Die Verbindung speichern wir in der
# Variable "connection".
#
# Über diese Verbindung können wir
# SQL-Abfragen ausführen.

connection = sqlite3.connect(DATABASE_PATH)


print("\n========================================")
print("GAME SALES ANALYTICS - SQL")
print("========================================")

print("\n=== SQL-ANALYSE GESTARTET ===")


# ============================================================
# 5. SQL-ABFRAGEN AUSFÜHREN
# ============================================================

# try:
#   Beginnt einen Codeabschnitt, in dem
#   unsere SQL-Abfragen durchgeführt werden.
#
# finally:
#   Wird am Ende immer ausgeführt,
#   auch wenn innerhalb des try-Blocks
#   ein Fehler auftritt.
#
# So stellen wir sicher, dass die
# Datenbankverbindung geschlossen wird.

try:

    # ========================================================
    # ANALYSE 1: DIE ERSTEN 10 SPIELE
    # ========================================================

    # SELECT *:
    #   Wählt alle Spalten unserer Tabelle aus.
    #
    # FROM games:
    #   Legt die Tabelle fest.
    #
    # ORDER BY Rank:
    #   Sortiert nach der ursprünglichen Rangfolge.
    #
    # LIMIT 10:
    #   Gibt maximal zehn Zeilen zurück.

    query = """
    SELECT *
    FROM games
    ORDER BY Rank ASC
    LIMIT 10;
    """

    # read_sql_query():
    #   Führt unsere SQL-Abfrage aus.
    #
    # Das Ergebnis wird als Pandas-DataFrame
    # gespeichert.

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== ERSTE 10 SPIELE ===")
    print(result)


    # ========================================================
    # ANALYSE 2: TOP 10 PS2-SPIELE
    # ========================================================

    # Wir suchen die zehn meistverkauften Spieleinträge
    # für die PlayStation 2.
    #
    # WHERE Platform = 'PS2':
    #   Filtert nach der gewünschten Plattform.
    #
    # ORDER BY Global_Sales DESC:
    #   Sortiert die Verkäufe absteigend.
    #
    # LIMIT 10:
    #   Begrenzt das Ergebnis auf zehn Spiele.

    query = """
    SELECT
        Name,
        Platform,
        Year,
        Global_Sales
    FROM games
    WHERE Platform = 'PS2'
    ORDER BY Global_Sales DESC
    LIMIT 10;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== TOP 10 PS2-SPIELE ===")
    print(result)


    # ========================================================
    # ANALYSE 3: VERKÄUFE NACH GENRE
    # ========================================================

    # GROUP BY Genre:
    #   Gruppiert alle Spiele nach ihrem Genre.
    #
    # COUNT(*):
    #   Zählt die Spieleinträge pro Genre.
    #
    # SUM(Global_Sales):
    #   Addiert die Verkaufszahlen innerhalb
    #   jeder Genre-Gruppe.
    #
    # ROUND(..., 2):
    #   Rundet die Ergebnisse auf zwei Nachkommastellen.
    #
    # AS Total_Sales:
    #   Vergibt einen Namen für die neue Ergebnisspalte.
    #
    # ORDER BY Total_Sales DESC:
    #   Sortiert nach den höchsten Gesamtverkäufen.

    query = """
    SELECT
        Genre,
        COUNT(*) AS Game_Count,
        ROUND(SUM(Global_Sales), 2) AS Total_Sales
    FROM games
    GROUP BY Genre
    ORDER BY Total_Sales DESC;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== VERKÄUFE NACH GENRE ===")
    print(result)


    # ========================================================
    # ANALYSE 4: TOP 10 SPIELE WELTWEIT
    # ========================================================

    # Wir suchen die zehn Spieleinträge
    # mit den höchsten weltweiten Verkaufszahlen.
    #
    # SELECT:
    #   Wählt nur die benötigten Spalten.
    #
    # ORDER BY Global_Sales DESC:
    #   Die höchsten Verkaufszahlen stehen zuerst.
    #
    # LIMIT 10:
    #   Gibt maximal zehn Spiele zurück.
    #
    # Hinweis:
    #   Ein Spiel kann auf mehreren Plattformen
    #   als separater Datensatz vorkommen.

    query = """
    SELECT
        Name,
        Platform,
        Genre,
        Global_Sales
    FROM games
    ORDER BY Global_Sales DESC
    LIMIT 10;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== TOP 10 SPIELE WELTWEIT ===")
    print(result)


    # ========================================================
    # ANALYSE 5: DURCHSCHNITTLICHE VERKÄUFE PRO GENRE
    # ========================================================

    # AVG():
    #   Berechnet den Durchschnitt einer Spalte.
    #
    # In unserem Fall berechnen wir:
    #
    #   Gesamtverkäufe des Genres
    #   ------------------------
    #   Anzahl der Spieleinträge
    #
    # Dadurch erkennen wir, wie viele Millionen
    # Exemplare ein Spieleintrag eines Genres
    # durchschnittlich verkauft hat.
    #
    # ROUND(AVG(Global_Sales), 2):
    #   Rundet den Durchschnitt auf zwei Stellen.
    #
    # GROUP BY Genre:
    #   Berechnet einen Durchschnitt pro Genre.

    query = """
    SELECT
        Genre,
        COUNT(*) AS Game_Count,
        ROUND(AVG(Global_Sales), 2) AS Average_Sales
    FROM games
    GROUP BY Genre
    ORDER BY Average_Sales DESC;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== DURCHSCHNITTLICHE VERKÄUFE PRO GENRE ===")
    print(result)


    # ========================================================
    # ANALYSE 6: GENRES MIT MINDESTENS 1000 SPIELEN
    # ========================================================

    # HAVING:
    #   Filtert bereits gruppierte Ergebnisse.
    #
    # Unterschied zwischen WHERE und HAVING:
    #
    # WHERE:
    #   Filtert einzelne Zeilen VOR der Gruppierung.
    #
    # HAVING:
    #   Filtert Gruppen NACH der Gruppierung.
    #
    # HAVING COUNT(*) >= 1000:
    #   Es werden nur Genres berücksichtigt,
    #   die mindestens 1000 Spieleinträge besitzen.
    #
    # SUM(Global_Sales):
    #   Addiert die Verkäufe dieser Genres.

    query = """
    SELECT
        Genre,
        COUNT(*) AS Game_Count,
        ROUND(SUM(Global_Sales), 2) AS Total_Sales
    FROM games
    GROUP BY Genre
    HAVING COUNT(*) >= 1000
    ORDER BY Total_Sales DESC;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== GENRES MIT MINDESTENS 1000 SPIELEN ===")
    print(result)


    # ========================================================
    # ANALYSE 7: TOP 10 PS3-ACTION-SPIELE AB 2010
    # ========================================================

    # Jetzt verwenden wir mehrere Filterbedingungen.
    #
    # WHERE:
    #   Beginnt unsere Filterung.
    #
    # Platform = 'PS3':
    #   Nur Spiele für PlayStation 3.
    #
    # AND Genre = 'Action':
    #   Zusätzlich nur Action-Spiele.
    #
    # AND Year >= 2010:
    #   Zusätzlich Erscheinungsjahr ab 2010.
    #
    # AND:
    #   Alle Bedingungen müssen gleichzeitig
    #   erfüllt sein.
    #
    # ORDER BY Global_Sales DESC:
    #   Sortiert nach den Verkaufszahlen.
    #
    # LIMIT 10:
    #   Zeigt maximal zehn Ergebnisse.

    query = """
    SELECT
        Name,
        Platform,
        Year,
        Genre,
        Global_Sales
    FROM games
    WHERE Platform = 'PS3'
      AND Genre = 'Action'
      AND Year >= 2010
    ORDER BY Global_Sales DESC
    LIMIT 10;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== TOP 10 PS3-ACTION-SPIELE AB 2010 ===")
    print(result)


    # ========================================================
    # ANALYSE 8: TOP 10 PUBLISHER NACH VERKÄUFEN
    # ========================================================

    # Wir untersuchen, welche Publisher insgesamt
    # die höchsten Verkaufszahlen haben.
    #
    # Publisher:
    #   Name des Herausgebers.
    #
    # COUNT(*):
    #   Anzahl der Spieleinträge des Publishers.
    #
    # SUM(Global_Sales):
    #   Gesamte weltweite Verkaufszahlen.
    #
    # WHERE Publisher != 'Unknown':
    #   Schließt unbekannte Publisher aus.
    #
    # GROUP BY Publisher:
    #   Fasst alle Einträge desselben Publishers
    #   zu einer Gruppe zusammen.

    query = """
    SELECT
        Publisher,
        COUNT(*) AS Game_Count,
        ROUND(SUM(Global_Sales), 2) AS Total_Sales
    FROM games
    WHERE Publisher != 'Unknown'
    GROUP BY Publisher
    ORDER BY Total_Sales DESC
    LIMIT 10;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== TOP 10 PUBLISHER ===")
    print(result)


    # ========================================================
    # ANALYSE 9: VERKÄUFE NACH REGION
    # ========================================================

    # Wir berechnen die gesamten Verkaufszahlen
    # für Nordamerika, Europa, Japan und
    # die übrigen Regionen.
    #
    # Hier benötigen wir kein GROUP BY,
    # weil wir die komplette Tabelle zusammenfassen.
    #
    # Jede SUM()-Funktion addiert eine
    # der regionalen Verkaufsspalten.

    query = """
    SELECT
        ROUND(SUM(NA_Sales), 2) AS North_America,
        ROUND(SUM(EU_Sales), 2) AS Europe,
        ROUND(SUM(JP_Sales), 2) AS Japan,
        ROUND(SUM(Other_Sales), 2) AS Other_Regions
    FROM games;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    print("\n=== VERKÄUFE NACH REGION ===")
    print(result)


# ============================================================
# 6. DATENBANKVERBINDUNG SCHLIESSEN
# ============================================================

finally:

    # Dieser Abschnitt wird auch ausgeführt,
    # wenn innerhalb des try-Blocks ein Fehler auftritt.
    #
    # close():
    #   Schließt die Verbindung zur SQLite-Datenbank.
    #
    # Dadurch werden Ressourcen freigegeben.

    connection.close()

    print("\nDatenbankverbindung geschlossen.")


# ============================================================
# 7. PROGRAMMENDE
# ============================================================

# Diese Meldung wird nur erreicht,
# wenn die SQL-Abfragen ohne unbehandelten
# Fehler abgeschlossen wurden.
#
# Bei einem Fehler im try-Block wird zuerst
# die Verbindung geschlossen und danach
# der Fehler von Python ausgegeben.

print("\n========================================")
print("SQL-ANALYSE ERFOLGREICH ABGESCHLOSSEN")
print("========================================")


# ============================================================
# ENDE DES MODULS
# ============================================================
#
# Unsere SQL-Analyse kann jetzt:
#
# 1. Alle Spiele einer Tabelle anzeigen.
#
# 2. Spiele nach Plattform filtern.
#
# 3. Verkaufszahlen nach Genre gruppieren.
#
# 4. Die erfolgreichsten Spiele ermitteln.
#
# 5. Durchschnittliche Verkäufe berechnen.
#
# 6. Gruppierte Ergebnisse mit HAVING filtern.
#
# 7. Mehrere Bedingungen mit AND kombinieren.
#
# 8. Publisher nach Gesamtverkäufen vergleichen.
#
# 9. Regionale Verkaufszahlen berechnen.
#
# Im nächsten Schritt verwenden wir diese Daten
# für unser interaktives Streamlit-Dashboard.
#
# ============================================================
