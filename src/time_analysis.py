
# ============================================================
# GAME SALES ANALYTICS
# MODUL: TIME ANALYSIS
# ============================================================
#
# Ziel:
#   Verkaufszahlen von Videospielen nach ihrem
#   Erscheinungsjahr untersuchen.
#
# Wir analysieren:
#   1. Weltweite Verkäufe nach Erscheinungsjahr
#   2. Erfolgreichste Erscheinungsjahre
#   3. Regionale Verkaufsentwicklung
#   4. Prozentuale Veränderungen zwischen Jahren
#
# WICHTIG:
#   Der Datensatz enthält Gesamtverkäufe einzelner
#   Spiele, gruppiert nach Erscheinungsjahr.
#   Er enthält KEINE jährlichen Verkaufstransaktionen.
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# Pandas:
#   Zum Einlesen, Gruppieren und Analysieren
#   unserer tabellarischen Daten.

import pandas as pd

# Matplotlib:
#   Zum Erstellen und Speichern von Diagrammen.

import matplotlib.pyplot as plt

# Path:
#   Zum zuverlässigen Arbeiten mit Datei- und
#   Ordnerpfaden auf verschiedenen Betriebssystemen.

from pathlib import Path


# ============================================================
# 2. PROJEKTPFADE FESTLEGEN
# ============================================================

# __file__ enthält den Pfad zu time_analysis.py.
#
# resolve():
#   Ermittelt den absoluten Dateipfad.
#
# parent.parent:
#   Geht vom Ordner src/ eine Ebene nach oben
#   in das Hauptverzeichnis unseres Projekts.

BASE_DIR = Path(__file__).resolve().parent.parent


# Wir verwenden die bereits bereinigten Daten.
#
# In Schritt 7 haben wir:
#   - fehlende Erscheinungsjahre entfernt
#   - Year in ganze Zahlen umgewandelt
#   - vollständig identische Duplikate entfernt
#   - fehlende Publisher gekennzeichnet

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "vgsales_clean.csv"
)


# Hier speichern wir unsere Diagramme.

IMAGES_DIR = BASE_DIR / "images"


# Sicherstellen, dass der Ordner existiert.
#
# exist_ok=True verhindert einen Fehler,
# falls der Ordner bereits vorhanden ist.

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. DATENSATZ LADEN
# ============================================================

print("\n=== ZEITREIHENANALYSE STARTEN ===")


# read_csv():
#   Liest unsere bereinigte CSV-Datei ein.
#
# Der DataFrame wird in "df" gespeichert.

df = pd.read_csv(DATA_PATH)


# Wir kontrollieren, ob die benötigten
# Spalten im Datensatz vorhanden sind.
#
# Diese Prüfung hilft uns, Fehler frühzeitig
# zu erkennen und verständlich auszugeben.

required_columns = [
    "Year",
    "Global_Sales",
    "NA_Sales",
    "EU_Sales",
    "JP_Sales"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Die benötigte Spalte '{column}' fehlt!"
        )


# ============================================================
# 4. DATEN AUF EINEN SINNVOLLEN ZEITRAUM BEGRENZEN
# ============================================================

# Der historische vgsales-Datensatz enthält auch
# vereinzelte Einträge für spätere Jahre.
#
# Für unsere erste historische Untersuchung
# betrachten wir deshalb die Jahre 1980 bis 2016.
#
# Das ist eine bewusste Einschränkung der Analyse.
# Sie macht den Datensatz nicht vollständig.
#
# between(1980, 2016):
#   Prüft für jede Zeile, ob das Jahr innerhalb
#   dieses Bereichs liegt (beide Grenzen inklusive).
#
# Das Ergebnis ist eine Liste aus True/False-Werten.
#
# Mit df[...] wählen wir nur die Zeilen aus,
# für die die Bedingung True ist.
#
# copy():
#   Erstellt eine unabhängige Kopie der Auswahl.

df_time = df[df["Year"].between(1980, 2016)].copy()


# Überprüfen, wie viele Spiele berücksichtigt werden.

print("\n=== ANALYSEZEITRAUM ===")

print("Von: 1980")
print("Bis: 2016")
print("Berücksichtigte Spiele:", len(df_time))


# ============================================================
# 5. WELTWEITE VERKÄUFE NACH ERSCHEINUNGSJAHR
# ============================================================

# groupby("Year"):
#   Gruppiert die Spiele nach Erscheinungsjahr.
#
# ["Global_Sales"]:
#   Wählt die weltweiten Gesamtverkäufe aus.
#
# sum():
#   Addiert die Verkaufszahlen der Spiele,
#   die im jeweiligen Jahr erschienen sind.
#
# sort_index():
#   Sortiert die Erscheinungsjahre aufsteigend.
#
# So entsteht eine Pandas-Series:
#
# Jahr    Gesamtverkäufe
# 1980    ...
# 1981    ...
# 1982    ...
#
# Alle Verkäufe sind in Millionen Exemplaren.

yearly_sales = (
    df_time.groupby("Year")["Global_Sales"]
    .sum()
    .sort_index()
)


print("\n=== WELTWEITE VERKÄUFE NACH JAHR ===")

print(yearly_sales)


# ============================================================
# 6. LINIENDIAGRAMM: WELTWEITE VERKÄUFE
# ============================================================

# Neue Zeichenfläche mit 12 Zoll Breite
# und 6 Zoll Höhe erstellen.

plt.figure(figsize=(12, 6))


# plot():
#   Erstellt standardmäßig ein Liniendiagramm.
#
# yearly_sales.index:
#   Erscheinungsjahre auf der X-Achse.
#
# yearly_sales.values:
#   Addierte Verkäufe auf der Y-Achse.
#
# marker="o":
#   Markiert jeden Datenpunkt mit einem Kreis.
#
# linewidth=2:
#   Macht die Linie etwas deutlicher sichtbar.

plt.plot(
    yearly_sales.index,
    yearly_sales.values,
    color="royalblue",
    marker="o",
    linewidth=2
)


# Diagramm beschriften.

plt.title("Weltweite Spieleverkäufe nach Erscheinungsjahr")

plt.xlabel("Erscheinungsjahr")

plt.ylabel("Verkäufe in Millionen")


# grid():
#   Aktiviert Hilfslinien im Diagramm.
#
# alpha=0.3:
#   Macht die Linien leicht transparent.

plt.grid(True, alpha=0.3)


# Automatische Abstände berechnen.

plt.tight_layout()


# Diagramm als PNG-Datei speichern.
#
# dpi=300 sorgt für eine hohe Auflösung.

plt.savefig(
    IMAGES_DIR / "yearly_global_sales.png",
    dpi=300
)


# Diagramm schließen.
#
# Dadurch öffnet sich kein zusätzliches Fenster.

plt.close()


print("\nDiagramm gespeichert: yearly_global_sales.png")


# ============================================================
# 7. DIE ERFOLGREICHSTEN ERSCHEINUNGSJAHRE
# ============================================================

# idxmax():
#   Gibt den Index des größten Wertes zurück.
#
# Da unser Index die Jahreszahlen enthält,
# erhalten wir das Erscheinungsjahr mit den
# höchsten aufsummierten Verkaufszahlen.

best_year = yearly_sales.idxmax()


# max():
#   Liefert den höchsten Verkaufswert.

best_year_sales = yearly_sales.max()


print("\n=== ERFOLGREICHSTES ERSCHEINUNGSJAHR ===")

print("Jahr:", best_year)

print("Verkäufe in Millionen:", round(best_year_sales, 2))


# sort_values(ascending=False):
#   Sortiert die Verkaufszahlen absteigend.
#
# head(10):
#   Wählt die zehn erfolgreichsten Jahre.

top_10_years = (
    yearly_sales
    .sort_values(ascending=False)
    .head(10)
)


print("\n=== TOP 10 ERSCHEINUNGSJAHRE ===")

print(top_10_years)


# ============================================================
# 8. REGIONALE VERKÄUFE NACH ERSCHEINUNGSJAHR
# ============================================================

# Wir wählen die drei großen Einzelmärkte
# Nordamerika, Europa und Japan aus.

region_columns = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales"
]


# Wir gruppieren erneut nach Erscheinungsjahr.
#
# Statt einer einzelnen Verkaufsspalte
# verwenden wir nun mehrere Spalten.
#
# sum():
#   Addiert die Verkäufe jeder Region getrennt.
#
# Das Ergebnis ist ein DataFrame mit:
#
# Year | NA_Sales | EU_Sales | JP_Sales

yearly_region_sales = (
    df_time.groupby("Year")[region_columns]
    .sum()
    .sort_index()
)


print("\n=== REGIONALE VERKÄUFE NACH JAHR ===")

print(yearly_region_sales)


# ============================================================
# 9. DIAGRAMM: REGIONALE VERKAUFSENTWICKLUNG
# ============================================================

# Eine neue Zeichenfläche erstellen.

plt.figure(figsize=(12, 6))


# Wir erstellen drei Linien in einem Diagramm.
#
# Jede Linie verwendet dieselben Jahreszahlen,
# aber unterschiedliche regionale Verkaufswerte.

plt.plot(
    yearly_region_sales.index,
    yearly_region_sales["NA_Sales"],
    label="Nordamerika",
    color="royalblue",
    linewidth=2
)

plt.plot(
    yearly_region_sales.index,
    yearly_region_sales["EU_Sales"],
    label="Europa",
    color="seagreen",
    linewidth=2
)

plt.plot(
    yearly_region_sales.index,
    yearly_region_sales["JP_Sales"],
    label="Japan",
    color="darkorange",
    linewidth=2
)


# Titel und Achsenbeschriftungen.

plt.title("Regionale Verkäufe nach Erscheinungsjahr")

plt.xlabel("Erscheinungsjahr")

plt.ylabel("Verkäufe in Millionen")


# legend():
#   Zeigt die Legende an.
#
# Die Texte stammen aus den label-Parametern
# unserer drei plt.plot()-Aufrufe.

plt.legend()


# Hilfslinien aktivieren.

plt.grid(True, alpha=0.3)


# Abstände optimieren.

plt.tight_layout()


# Diagramm speichern.

plt.savefig(
    IMAGES_DIR / "yearly_regional_sales.png",
    dpi=300
)


# Zeichenfläche schließen.

plt.close()


print("Diagramm gespeichert: yearly_regional_sales.png")


# ============================================================
# 10. PROZENTUALE VERÄNDERUNGEN BERECHNEN
# ============================================================

# pct_change():
#   Berechnet die relative Veränderung zwischen
#   einem Wert und dem vorherigen Wert.
#
# Beispiel:
#
# Vorjahr:       100 Millionen
# Aktuelles Jahr: 120 Millionen
#
# Rechnung:
#   (120 - 100) / 100 = 0.20
#
# Das entspricht einem Anstieg um 20 Prozent.
#
# mul(100):
#   Wandelt die Dezimalzahl in Prozent um.
#
# Der erste Wert wird NaN sein,
# weil kein Vorjahr innerhalb unserer
# Zeitreihe vorhanden ist.

yearly_growth = yearly_sales.pct_change().mul(100)


print("\n=== VERÄNDERUNG GEGENÜBER DEM VORJAHR ===")

print(yearly_growth.round(2))


# ============================================================
# 11. DIAGRAMM: PROZENTUALE VERÄNDERUNGEN
# ============================================================

# Wir erstellen erneut eine Zeichenfläche.

plt.figure(figsize=(12, 6))


# Die prozentualen Veränderungen stellen
# wir als vertikale Balken dar.
#
# Positive Werte bedeuten einen Anstieg,
# negative Werte einen Rückgang.

plt.bar(
    yearly_growth.index,
    yearly_growth.values,
    color="mediumpurple"
)


# axhline():
#   Zeichnet eine horizontale Linie.
#
# y=0:
#   Die Linie liegt bei 0 Prozent.
#
# Damit lassen sich positive und negative
# Veränderungen leichter unterscheiden.

plt.axhline(
    y=0,
    color="black",
    linewidth=1
)


# Diagramm beschriften.

plt.title("Veränderung der Verkäufe nach Erscheinungsjahr")

plt.xlabel("Erscheinungsjahr")

plt.ylabel("Veränderung zum Vorjahr in %")


# Hilfslinien aktivieren.

plt.grid(axis="y", alpha=0.3)


# Layout anpassen.

plt.tight_layout()


# Diagramm speichern.

plt.savefig(
    IMAGES_DIR / "yearly_sales_growth.png",
    dpi=300
)


# Diagramm schließen.

plt.close()


print("Diagramm gespeichert: yearly_sales_growth.png")


# ============================================================
# 12. ANALYSEERGEBNISSE ALS CSV SPEICHERN
# ============================================================

# Wir möchten die aggregierten Jahresdaten später
# auch in unserer SQL-Datenbank verwenden.
#
# Daher speichern wir die Berechnungen zusätzlich
# in einer neuen CSV-Datei.

OUTPUT_PATH = (
    BASE_DIR / "data" / "processed" / "yearly_sales.csv"
)


# to_frame():
#   Wandelt eine Pandas-Series in einen
#   DataFrame um.
#
# name="Global_Sales":
#   Legt den Namen der Verkaufsspalte fest.
#
# reset_index():
#   Wandelt den bisherigen Index "Year"
#   wieder in eine normale Tabellenspalte um.

yearly_sales_df = (
    yearly_sales
    .to_frame(name="Global_Sales")
    .reset_index()
)


# Eine neue Spalte mit der prozentualen
# Veränderung hinzufügen.
#
# to_numpy():
#   Liefert die Werte in ihrer bisherigen
#   Reihenfolge ohne den Pandas-Index.
#
# Da beide Series aus derselben sortierten
# Jahresreihe stammen, stimmen die Positionen
# der Werte überein.

yearly_sales_df["Growth_Percent"] = yearly_growth.to_numpy()


# Die Ergebnisse als CSV-Datei speichern.

yearly_sales_df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nJahresdaten gespeichert:", OUTPUT_PATH)


# ============================================================
# 13. PROGRAMMENDE
# ============================================================

print("\n========================================")
print("ZEITREIHENANALYSE ABGESCHLOSSEN")
print("========================================")
