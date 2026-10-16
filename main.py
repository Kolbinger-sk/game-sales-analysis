
# ============================================================
# GAME SALES ANALYTICS
# ============================================================
#
# Projekt:
#   Analyse weltweiter Videospiel-Verkaufszahlen
#
# Programmiersprache:
#   Python
#
# Verwendete Bibliotheken:
#   - pandas: Einlesen, Bereinigen und Analysieren von Daten
#   - matplotlib: Erstellen und Speichern von Diagrammen
#   - pathlib: Arbeiten mit Datei- und Ordnerpfaden
#
# Aktueller Projektstand:
#   Schritt 1 bis Schritt 7
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# Pandas ermöglicht uns die Arbeit mit Tabellen (DataFrames).
#
# Mit "as pd" geben wir Pandas einen kürzeren Namen.

import pandas as pd


# Matplotlib verwenden wir für Diagramme.
#
# pyplot enthält Funktionen zum Erstellen,
# Beschriften und Speichern von Diagrammen.

import matplotlib.pyplot as plt


# Path stammt aus der Python-Standardbibliothek.
#
# Damit können wir Datei- und Ordnerpfade erstellen,
# ohne auf Unterschiede zwischen Windows,
# macOS und Linux achten zu müssen.

from pathlib import Path


# ============================================================
# 2. PROJEKTPFADE FESTLEGEN
# ============================================================

# __file__:
#   Enthält den Dateipfad unserer main.py.
#
# Path(__file__).resolve():
#   Ermittelt den absoluten Dateipfad.
#
# .parent:
#   Gibt den übergeordneten Ordner zurück.
#
# Da main.py direkt im Projektordner liegt,
# erhalten wir damit unseren Hauptordner.

BASE_DIR = Path(__file__).resolve().parent


# Pfad zu unserer unveränderten Originaldatei.

RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "vgsales.csv"


# Pfad zur späteren bereinigten CSV-Datei.

CLEAN_DATA_PATH = (
    BASE_DIR / "data" / "processed" / "vgsales_clean.csv"
)


# Speicherordner für unsere Diagramme.

IMAGES_DIR = BASE_DIR / "images"


# mkdir():
#   Erstellt einen Ordner.
#
# parents=True:
#   Erstellt auch übergeordnete Ordner, falls nötig.
#
# exist_ok=True:
#   Verhindert einen Fehler, wenn der Ordner
#   bereits existiert.

IMAGES_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_DATA_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. DATENSATZ LADEN
# ============================================================

print("\n=== DATENSATZ LADEN ===")


# read_csv():
#   Liest unsere CSV-Datei ein.
#
# Das Ergebnis wird als DataFrame gespeichert.
#
# Ein DataFrame ist eine Tabelle, die aus
# Zeilen und Spalten besteht.
#
# Wir speichern die Daten in der Variable "df".

df = pd.read_csv(RAW_DATA_PATH)


# Ausgabe zur Kontrolle.

print("Datensatz erfolgreich geladen!")


# ============================================================
# 4. ERSTE FÜNF SPIELE ANZEIGEN
# ============================================================

print("\n=== ERSTE 5 SPIELE ===")


# head():
#   Zeigt standardmäßig die ersten fünf Zeilen.
#
# Dadurch bekommen wir einen ersten Eindruck
# von den vorhandenen Daten.

print(df.head())


# ============================================================
# 5. GRÖSSE DES DATENSATZES
# ============================================================

print("\n=== DATENSATZ-GRÖSSE ===")


# shape:
#   Liefert ein Tupel mit zwei Werten.
#
# shape[0]:
#   Anzahl der Zeilen.
#
# shape[1]:
#   Anzahl der Spalten.
#
# Bei unserem Datensatz erwarten wir
# ungefähr 16.598 Zeilen und 11 Spalten.

print("Anzahl der Spiele:", df.shape[0])

print("Anzahl der Spalten:", df.shape[1])


# ============================================================
# 6. INFORMATIONEN ÜBER DEN DATENSATZ
# ============================================================

print("\n=== DATENSATZ-INFORMATIONEN ===")


# info():
#   Zeigt verschiedene Informationen an:
#
#   - Spaltennamen
#   - Anzahl vorhandener Werte
#   - Datentypen
#   - Speicherverbrauch
#
# Wichtige Datentypen:
#
# int64:
#   Ganze Zahlen.
#
# float64:
#   Dezimalzahlen.
#
# object:
#   Häufig Texte beziehungsweise Zeichenketten.

df.info()


# ============================================================
# 7. STATISTISCHE ZUSAMMENFASSUNG
# ============================================================

print("\n=== STATISTISCHE ZUSAMMENFASSUNG ===")


# describe():
#   Erstellt statistische Kennzahlen
#   für unsere numerischen Spalten.
#
# count:
#   Anzahl vorhandener Werte.
#
# mean:
#   Durchschnitt.
#
# std:
#   Standardabweichung.
#
# min:
#   Kleinster Wert.
#
# 25%, 50%, 75%:
#   Quartile der Datenverteilung.
#
# max:
#   Größter Wert.

print(df.describe())


# ============================================================
# 8. ANZAHL VERSCHIEDENER GENRES
# ============================================================

print("\n=== ANZAHL DER GENRES ===")


# df["Genre"]:
#   Wählt die Spalte "Genre" aus.
#
# nunique():
#   Zählt die unterschiedlichen Werte.
#
# Unser Datensatz enthält 12 Genres.

genre_count = df["Genre"].nunique()


# Ergebnis ausgeben.

print("Anzahl verschiedener Genres:", genre_count)


# ============================================================
# 9. ANZAHL DER SPIELE PRO GENRE
# ============================================================

print("\n=== SPIELE PRO GENRE ===")


# value_counts():
#   Zählt, wie häufig jeder Wert vorkommt.
#
# In unserem Fall:
#   Wie viele Spiele gehören zu jedem Genre?
#
# Die Werte werden automatisch absteigend sortiert.
#
# Das Genre mit den meisten Spielen steht oben.

genre_counts = df["Genre"].value_counts()


# Ergebnis ausgeben.

print(genre_counts)


# ============================================================
# 10. TOP 5 GENRES
# ============================================================

print("\n=== TOP 5 GENRES ===")


# head(5):
#   Zeigt nur die ersten fünf Einträge.
#
# Da unsere Genres bereits nach Häufigkeit
# sortiert sind, erhalten wir die Top 5.

print(genre_counts.head(5))


# ============================================================
# 11. DIAGRAMM: ANZAHL DER SPIELE PRO GENRE
# ============================================================

# figure():
#   Erstellt eine neue Zeichenfläche.
#
# figsize=(12, 6):
#   Breite: 12 Zoll
#   Höhe:    6 Zoll

plt.figure(figsize=(12, 6))


# bar():
#   Erstellt ein vertikales Balkendiagramm.
#
# genre_counts.index:
#   Enthält die Namen der Genres.
#
# genre_counts.values:
#   Enthält die Anzahl der Spiele.
#
# color:
#   Bestimmt die Farbe der Balken.

plt.bar(
    genre_counts.index,
    genre_counts.values,
    color="steelblue"
)


# Titel und Achsenbeschriftungen.

plt.title("Anzahl der Spiele pro Genre")

plt.xlabel("Genre")

plt.ylabel("Anzahl der Spiele")


# xticks():
#   Verändert die Beschriftungen der X-Achse.
#
# rotation=45:
#   Dreht die Genre-Namen um 45 Grad.
#
# ha="right":
#   Richtet die Beschriftungen rechtsbündig aus.

plt.xticks(rotation=45, ha="right")


# tight_layout():
#   Optimiert automatisch die Abstände.

plt.tight_layout()


# savefig():
#   Speichert unser Diagramm als Bild.
#
# dpi=300:
#   Sorgt für eine hohe Auflösung.

plt.savefig(
    IMAGES_DIR / "genre_counts.png",
    dpi=300
)


# close():
#   Schließt die Matplotlib-Zeichenfläche.
#
# Dadurch wird kein Diagrammfenster geöffnet.
#
# Außerdem werden Ressourcen freigegeben.
#
# Wir verwenden absichtlich nicht plt.show(),
# da sonst mehrere Fenster erscheinen würden.

plt.close()


print("\nDiagramm gespeichert: genre_counts.png")


# ============================================================
# 12. WELTWEITE VERKÄUFE NACH GENRE
# ============================================================

print("\n=== WELTWEITE VERKÄUFE NACH GENRE ===")


# Wir untersuchen jetzt die Verkaufszahlen.
#
# groupby("Genre"):
#   Gruppiert alle Spiele nach Genre.
#
# ["Global_Sales"]:
#   Wählt die weltweiten Verkaufszahlen aus.
#
# sum():
#   Addiert die Verkäufe innerhalb jedes Genres.
#
# sort_values(ascending=False):
#   Sortiert die Ergebnisse absteigend.
#
# Die Verkaufszahlen sind in Millionen
# verkauften Exemplaren angegeben.

genre_sales = (
    df.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
)


# Ergebnis ausgeben.

print(genre_sales)


# ============================================================
# 13. DIAGRAMM: WELTWEITE VERKÄUFE NACH GENRE
# ============================================================

# Neue Zeichenfläche erstellen.

plt.figure(figsize=(12, 6))


# Balkendiagramm erstellen.
#
# X-Achse:
#   Genres.
#
# Y-Achse:
#   Weltweite Verkäufe in Millionen.

plt.bar(
    genre_sales.index,
    genre_sales.values,
    color="seagreen"
)


# Diagramm beschriften.

plt.title("Weltweite Verkäufe nach Genre")

plt.xlabel("Genre")

plt.ylabel("Verkäufe in Millionen")


# Beschriftungen drehen.

plt.xticks(rotation=45, ha="right")


# Layout optimieren.

plt.tight_layout()


# Diagramm als PNG speichern.

plt.savefig(
    IMAGES_DIR / "genre_sales.png",
    dpi=300
)


# Zeichenfläche schließen.

plt.close()


print("Diagramm gespeichert: genre_sales.png")


# ============================================================
# 14. FEHLENDE WERTE UNTERSUCHEN
# ============================================================

print("\n=== FEHLENDE WERTE ===")


# isnull():
#   Prüft jede Zelle auf fehlende Werte.
#
# Fehlender Wert:
#   True.
#
# Vorhandener Wert:
#   False.
#
# sum():
#   Zählt die True-Werte pro Spalte.
#
# So finden wir heraus, in welchen Spalten
# Daten fehlen.

missing_values = df.isnull().sum()


# Ergebnisse anzeigen.

print(missing_values)


# ============================================================
# 15. KOPIE FÜR DIE DATENBEREINIGUNG ERSTELLEN
# ============================================================

print("\n=== DATENBEREINIGUNG STARTEN ===")


# copy():
#   Erstellt eine unabhängige Kopie.
#
# Dadurch bleibt unser Original-DataFrame
# in der Variable "df" unverändert.
#
# Die bereinigten Daten werden in
# der Variable "df_clean" gespeichert.

df_clean = df.copy()


# ============================================================
# 16. FEHLENDE ERSCHEINUNGSJAHRE ENTFERNEN
# ============================================================

# dropna():
#   Entfernt Zeilen mit fehlenden Werten.
#
# subset=["Year"]:
#   Berücksichtigt dabei ausschließlich
#   die Spalte "Year".
#
# Spiele ohne Erscheinungsjahr werden entfernt.
#
# Wichtig:
#   Diese bereinigte Version eignet sich
#   besonders für zeitbasierte Analysen.
#
# Für Analysen ohne Jahresbezug können wir
# weiterhin den vollständigen Datensatz nutzen.

df_clean = df_clean.dropna(subset=["Year"])


# Anzahl der verbliebenen Spiele ausgeben.

print(
    "Spiele nach Entfernung fehlender Jahre:",
    df_clean.shape[0]
)


# ============================================================
# 17. DATENTYP DER ERSCHEINUNGSJAHRE KORRIGIEREN
# ============================================================

print("\n=== DATENTYPEN KORRIGIEREN ===")


# dtype:
#   Zeigt den aktuellen Datentyp.
#
# Wegen fehlender Jahreswerte verwendet Pandas
# ursprünglich häufig float64.

print("Datentyp vorher:", df_clean["Year"].dtype)


# astype(int):
#   Wandelt Werte in ganze Zahlen um.
#
# Beispiel:
#   2006.0 wird zu 2006.
#
# Das funktioniert hier, weil wir zuvor
# alle fehlenden Jahreswerte entfernt haben
# und die vorhandenen Jahreswerte ganzzahlig sind.

df_clean["Year"] = df_clean["Year"].astype(int)


# Neuen Datentyp ausgeben.

print("Datentyp nachher:", df_clean["Year"].dtype)


# ============================================================
# 18. DUPLIKATE UNTERSUCHEN
# ============================================================

print("\n=== DUPLIKATE UNTERSUCHEN ===")


# duplicated():
#   Erkennt mehrfach vorhandene Zeilen.
#
# Standardmäßig werden alle Spalten verglichen.
#
# Die erste Zeile bleibt unmarkiert.
# Jede weitere identische Zeile wird
# als Duplikat erkannt.
#
# sum():
#   Zählt alle erkannten Duplikate.

duplicates = df_clean.duplicated().sum()


# Anzahl ausgeben.

print("Gefundene Duplikate:", duplicates)


# drop_duplicates():
#   Entfernt vollständig identische Zeilen.
#
# Wir vergleichen bewusst alle Spalten.
#
# Zwei Spiele mit demselben Namen sind
# nicht automatisch Duplikate.
#
# Ein Spiel kann beispielsweise auf
# verschiedenen Plattformen erscheinen.

df_clean = df_clean.drop_duplicates()


# Noch einmal prüfen.

print(
    "Duplikate nach Bereinigung:",
    df_clean.duplicated().sum()
)


# ============================================================
# 19. FEHLENDE PUBLISHER BEHANDELN
# ============================================================

print("\n=== FEHLENDE PUBLISHER BEHANDELN ===")


# Zunächst zählen wir fehlende Publisher.

missing_publishers = df_clean["Publisher"].isnull().sum()


# Anzahl vor der Bereinigung.

print("Fehlende Publisher vorher:", missing_publishers)


# fillna():
#   Ersetzt fehlende Werte.
#
# Hier ersetzen wir fehlende Publisher
# durch den Text "Unknown".
#
# Dadurch bleiben die entsprechenden
# Verkaufsdaten erhalten.
#
# "Unknown" bedeutet dabei nur,
# dass der Publisher nicht bekannt ist.

df_clean["Publisher"] = (
    df_clean["Publisher"].fillna("Unknown")
)


# Erneut überprüfen.

print(
    "Fehlende Publisher nachher:",
    df_clean["Publisher"].isnull().sum()
)


# ============================================================
# 20. DATENBEREINIGUNG KONTROLLIEREN
# ============================================================

print("\n=== VERGLEICH DER DATENSÄTZE ===")


# Anzahl der Zeilen vor der Bereinigung.

original_rows = df.shape[0]


# Anzahl der Zeilen nach der Bereinigung.

clean_rows = df_clean.shape[0]


# Differenz berechnen.
#
# Dadurch erfahren wir, wie viele Zeilen
# insgesamt entfernt wurden.

removed_rows = original_rows - clean_rows


# Ergebnisse ausgeben.

print("Spiele vorher:", original_rows)

print("Spiele nachher:", clean_rows)

print("Entfernte Zeilen:", removed_rows)


# ============================================================
# 21. BEREINIGTE DATEN SPEICHERN
# ============================================================

print("\n=== BEREINIGTE DATEN SPEICHERN ===")


# to_csv():
#   Speichert einen DataFrame als CSV-Datei.
#
# CLEAN_DATA_PATH:
#   Enthält den vollständigen Speicherpfad:
#
#   data/processed/vgsales_clean.csv
#
# index=False:
#   Verhindert, dass Pandas zusätzliche
#   DataFrame-Zeilennummern in die CSV schreibt.
#
# Die ursprüngliche Datei im Ordner "raw"
# bleibt dabei unverändert.

df_clean.to_csv(
    CLEAN_DATA_PATH,
    index=False
)


# Bestätigung ausgeben.

print("Bereinigte CSV-Datei erfolgreich gespeichert!")

print("Dateipfad:", CLEAN_DATA_PATH)


# ============================================================
# 22. PROGRAMM ABSCHLIESSEN
# ============================================================

print("\n========================================")
print("GAME SALES ANALYTICS")
print("ALLE ANALYSEN ERFOLGREICH ABGESCHLOSSEN")
print("========================================")


