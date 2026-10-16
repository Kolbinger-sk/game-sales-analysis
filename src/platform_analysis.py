
# ============================================================
# GAME SALES ANALYTICS
# MODUL: PLATFORM ANALYSIS
# ============================================================
#
# Ziel:
#   Verkaufszahlen verschiedener Gaming-Plattformen
#   analysieren und vergleichen.
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# Pandas wird verwendet, um unsere CSV-Datei einzulesen
# und Verkaufszahlen nach Plattform zu gruppieren.

import pandas as pd

# Matplotlib ermöglicht uns das Erstellen von Diagrammen.

import matplotlib.pyplot as plt

# Path hilft uns dabei, Dateipfade zuverlässig zu erstellen.

from pathlib import Path


# ============================================================
# 2. DATEIPFADE FESTLEGEN
# ============================================================

# __file__ enthält den Pfad zu platform_analysis.py.
#
# .resolve() erstellt einen absoluten Dateipfad.
#
# .parent gibt den übergeordneten Ordner zurück:
#   src/
#
# Mit dem zweiten .parent gelangen wir zum
# Hauptordner unseres Projekts.

BASE_DIR = Path(__file__).resolve().parent.parent

# Wir verwenden die Originaldaten für die
# Plattformanalyse, damit uns keine Verkaufszahlen
# wegen fehlender Erscheinungsjahre verloren gehen.

DATA_PATH = BASE_DIR / "data" / "raw" / "vgsales.csv"

# Speicherort für die Diagramme.

IMAGES_DIR = BASE_DIR / "images"

# Sicherstellen, dass der Bilderordner existiert.

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. DATENSATZ LADEN
# ============================================================

# read_csv() liest unsere CSV-Datei ein.
#
# Der DataFrame wird in der Variable df gespeichert.

df = pd.read_csv(DATA_PATH)

print("\n=== PLATTFORM-ANALYSE ===")


# ============================================================
# 4. VERKAUFSZAHLEN NACH PLATTFORM
# ============================================================

# groupby("Platform"):
#   Gruppiert alle Spiele nach ihrer Plattform.
#
# ["Global_Sales"]:
#   Wählt die weltweiten Verkaufszahlen aus.
#
# sum():
#   Addiert die Verkäufe innerhalb jeder Plattform.
#
# sort_values(ascending=False):
#   Sortiert die Verkaufszahlen vom größten
#   zum kleinsten Wert.

platform_sales = (
    df.groupby("Platform")["Global_Sales"]
    .sum()
    .sort_values(ascending=False)
)

# head(10):
#   Wählt die zehn Plattformen mit den
#   höchsten Gesamtverkäufen aus.

top_10_platforms = platform_sales.head(10)

print("\n=== TOP 10 PLATTFORMEN NACH VERKÄUFEN ===")

print(top_10_platforms)


# ============================================================
# 5. BALKENDIAGRAMM ERSTELLEN
# ============================================================

# Wir erstellen eine Zeichenfläche.
#
# figsize=(12, 6):
#   Breite: 12 Zoll
#   Höhe: 6 Zoll

plt.figure(figsize=(12, 6))

# Balkendiagramm erstellen.
#
# index:
#   Namen der Plattformen.
#
# values:
#   Weltweite Verkäufe in Millionen Exemplaren.

plt.bar(
    top_10_platforms.index,
    top_10_platforms.values,
    color="royalblue"
)

# Diagrammtitel und Achsenbeschriftungen.

plt.title("Top 10 Gaming-Plattformen nach Verkäufen")

plt.xlabel("Plattform")

plt.ylabel("Verkäufe in Millionen")

# Layout automatisch anpassen.

plt.tight_layout()

# Diagramm als PNG-Datei speichern.

plt.savefig(
    IMAGES_DIR / "top_10_platforms.png",
    dpi=300
)

# Zeichenfläche schließen, ohne ein Fenster zu öffnen.

plt.close()

print("\nDiagramm gespeichert: top_10_platforms.png")
