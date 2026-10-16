
# ============================================================
# GAME SALES ANALYTICS
# MODUL: REGIONAL ANALYSIS
# ============================================================
#
# Ziel:
#   Verkaufszahlen verschiedener Regionen analysieren.
#
# Untersuchte Regionen:
#   - Nordamerika (NA)
#   - Europa (EU)
#   - Japan (JP)
#   - Andere Regionen (Other)
#
# Alle Verkaufszahlen sind in Millionen Exemplaren.
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# Pandas ermöglicht uns die Analyse tabellarischer Daten.

import pandas as pd

# Matplotlib verwenden wir für unsere Diagramme.

import matplotlib.pyplot as plt

# Path hilft beim Erstellen von Datei- und Ordnerpfaden.

from pathlib import Path


# ============================================================
# 2. PROJEKTPFADE FESTLEGEN
# ============================================================

# __file__:
#   Pfad der aktuellen Python-Datei.
#
# .resolve():
#   Wandelt den Pfad in einen absoluten Pfad um.
#
# .parent.parent:
#   Geht zwei Verzeichnisebenen nach oben.
#
# Von:
#   game-sales-analysis/src/regional_analysis.py
#
# Zu:
#   game-sales-analysis/

BASE_DIR = Path(__file__).resolve().parent.parent


# Wir verwenden die Originaldaten, damit keine
# Verkaufszahlen durch unsere Jahresbereinigung fehlen.

DATA_PATH = BASE_DIR / "data" / "raw" / "vgsales.csv"


# Speicherort für unsere Diagramme.

IMAGES_DIR = BASE_DIR / "images"


# Den Ordner erstellen, falls er noch nicht existiert.

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. DATENSATZ LADEN
# ============================================================

print("\n=== REGIONALE VERKAUFSANALYSE ===")


# read_csv():
#   Liest die CSV-Datei in einen Pandas-DataFrame ein.

df = pd.read_csv(DATA_PATH)


# ============================================================
# 4. SPALTEN FÜR REGIONALE VERKÄUFE FESTLEGEN
# ============================================================

# Wir erstellen eine Liste mit den vier Spalten,
# die regionale Verkaufszahlen enthalten.
#
# Listen in Python werden mit eckigen Klammern
# geschrieben.
#
# Dadurch können wir mehrere Spalten gleichzeitig
# auswählen und analysieren.

region_columns = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales"
]


# ============================================================
# 5. GESAMTVERKÄUFE PRO REGION BERECHNEN
# ============================================================

# df[region_columns]:
#   Wählt alle vier regionalen Verkaufsspalten aus.
#
# sum():
#   Addiert standardmäßig die Werte jeder Spalte.
#
# Das Ergebnis ist eine Pandas-Series mit
# den Gesamtverkäufen pro Region.

regional_sales = df[region_columns].sum()


# Ergebnis anzeigen.

print("\n=== GESAMTVERKÄUFE PRO REGION ===")

print(regional_sales)


# ============================================================
# 6. REGIONALE VERKÄUFE ALS DIAGRAMM
# ============================================================

# Neue Zeichenfläche mit einer Breite von
# 10 Zoll und einer Höhe von 6 Zoll erstellen.

plt.figure(figsize=(10, 6))


# Wir erstellen ein Balkendiagramm.
#
# regional_sales.index:
#   Enthält die Spaltennamen der Regionen.
#
# regional_sales.values:
#   Enthält die aufsummierten Verkaufszahlen.
#
# Jeder Balken erhält dieselbe Farbe.

plt.bar(
    regional_sales.index,
    regional_sales.values,
    color="cornflowerblue"
)


# Titel und Achsen festlegen.

plt.title("Weltweite Spieleverkäufe nach Region")

plt.xlabel("Region")

plt.ylabel("Verkäufe in Millionen")


# Layout automatisch anpassen.

plt.tight_layout()


# Diagramm als PNG speichern.

plt.savefig(
    IMAGES_DIR / "regional_sales.png",
    dpi=300
)


# Diagramm schließen, ohne ein Fenster anzuzeigen.

plt.close()


print("\nDiagramm gespeichert: regional_sales.png")


# ============================================================
# 7. BELIEBTESTE GENRES NACH REGION
# ============================================================

print("\n=== VERKAUFSZAHLEN NACH GENRE UND REGION ===")


# groupby("Genre"):
#   Gruppiert alle Spiele nach ihrem Genre.
#
# [region_columns]:
#   Wählt die regionalen Verkaufsspalten aus.
#
# sum():
#   Addiert die Verkäufe jedes Genres pro Region.
#
# Das Ergebnis ist ein neuer DataFrame.
#
# Jede Zeile steht für ein Genre.
# Jede Spalte steht für eine Verkaufsregion.

genre_region_sales = (
    df.groupby("Genre")[region_columns]
    .sum()
)


# Den DataFrame im Terminal ausgeben.

print(genre_region_sales)


# ============================================================
# 8. VERKAUFSSTÄRKSTE GENRES PRO REGION
# ============================================================

# Wir betrachten die drei größten Einzelmärkte
# Nordamerika, Europa und Japan.
#
# Die Kategorie "Other" können wir später
# zusätzlich untersuchen.

for region in ["NA_Sales", "EU_Sales", "JP_Sales"]:

    # Eine Überschrift für die aktuelle Region ausgeben.

    print(f"\n=== TOP 5 GENRES: {region} ===")

    # Wir wählen die aktuelle Regionsspalte aus.
    #
    # sort_values(ascending=False):
    #   Sortiert die Genres nach ihren Verkaufszahlen.
    #
    # head(5):
    #   Liefert die fünf erfolgreichsten Genres.

    top_genres = (
        genre_region_sales[region]
        .sort_values(ascending=False)
        .head(5)
    )

    # Das Ergebnis im Terminal anzeigen.

    print(top_genres)


# ============================================================
# 9. VERGLEICH DER REGIONEN IN EINEM DIAGRAMM
# ============================================================

# Wir wollen die Verkäufe je Genre für Nordamerika,
# Europa und Japan direkt vergleichen.
#
# Dazu wählen wir die drei Spalten aus.

comparison_columns = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales"
]


# Wir sortieren die Genres nach ihren
# weltweiten Verkäufen.
#
# groupby("Genre"):
#   Fasst alle Spiele desselben Genres zusammen.
#
# ["Global_Sales"]:
#   Wählt die weltweiten Verkaufszahlen aus.
#
# sum():
#   Berechnet die Gesamtverkäufe je Genre.
#
# sort_values():
#   Sortiert vom höchsten zum niedrigsten Wert.
#
# .index:
#   Liefert die sortierten Genre-Namen.

genre_order = (
    df.groupby("Genre")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
    .index
)


# Mit .loc wählen wir die Genres in der
# zuvor berechneten Reihenfolge aus.
#
# Anschließend wählen wir nur die drei
# Vergleichsregionen.

comparison_data = genre_region_sales.loc[
    genre_order,
    comparison_columns
]


# Pandas bietet eine eigene plot()-Funktion.
#
# kind="bar":
#   Erstellt ein vertikales Balkendiagramm.
#
# Da mehrere Spalten vorhanden sind,
# werden für jedes Genre mehrere Balken angezeigt.
#
# figsize:
#   Bestimmt die Größe der Grafik.
#
# color:
#   Legt die Farben der drei Regionen fest.

ax = comparison_data.plot(
    kind="bar",
    figsize=(14, 7),
    color=["royalblue", "seagreen", "darkorange"]
)


# ax ist unser Achsenobjekt.
#
# Über dieses Objekt können wir das Diagramm
# direkt beschriften und konfigurieren.

ax.set_title("Genre-Verkäufe: Nordamerika, Europa und Japan")

ax.set_xlabel("Genre")

ax.set_ylabel("Verkäufe in Millionen")


# Legende hinzufügen, damit die Farben
# eindeutig einer Region zugeordnet werden.

ax.legend(
    ["Nordamerika", "Europa", "Japan"]
)


# Genre-Namen drehen.

plt.xticks(rotation=45, ha="right")


# Layout anpassen.

plt.tight_layout()


# Diagramm speichern.

plt.savefig(
    IMAGES_DIR / "genre_region_comparison.png",
    dpi=300
)


# Diagramm schließen.

plt.close()


print("Diagramm gespeichert: genre_region_comparison.png")


# ============================================================
# 10. PROGRAMMENDE
# ============================================================

print("\n=== REGIONALE ANALYSE ABGESCHLOSSEN ===")
