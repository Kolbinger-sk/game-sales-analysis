
# ============================================================
# GAME SALES ANALYTICS
# DASHBOARD VERSION 1.3
# ============================================================
#
# Projekt:
#   Analyse historischer Videospiel-Verkaufszahlen
#
# Technologien:
#   - Python
#   - Pandas
#   - SQLite
#   - Streamlit
#   - Plotly
#
# Funktionen:
#   1. Zentraler Datenbankzugriff
#   2. Genre-Filter
#   3. Plattform-Filter
#   4. Zeitraumfilter
#   5. Dynamische Kennzahlen
#   6. Genre-Verkaufsdiagramm
#   7. Regionale Verkaufsanalyse
#   8. Top-10-Spiele-Ranking
#   9. Zeitreihenanalyse
#   10. Interaktive Spieletabelle
#   11. CSV-Download
#
# ============================================================


# ============================================================
# 1. BIBLIOTHEKEN IMPORTIEREN
# ============================================================

# Streamlit erstellt unsere Weboberfläche.
import streamlit as st

# Pandas wird für die Datenverarbeitung verwendet.
import pandas as pd

# Plotly Express erstellt interaktive Diagramme.
import plotly.express as px

# sqlite3 benötigen wir zur Behandlung von Datenbankfehlern.
import sqlite3

# Unsere eigene Funktion aus dashboard/data_loader.py.
#
# Damit benötigen wir in dieser Datei
# keinen eigenen SQL-Verbindungscode mehr.
from data_loader import load_data


# ============================================================
# 2. STREAMLIT KONFIGURIEREN
# ============================================================

# set_page_config():
#   Legt das Aussehen und Verhalten der Seite fest.
#
# page_title:
#   Titel des Browser-Tabs.
#
# page_icon:
#   Symbol des Browser-Tabs.
#
# layout="wide":
#   Nutzt die verfügbare Bildschirmbreite.
#
# initial_sidebar_state="expanded":
#   Öffnet die Seitenleiste beim Start.

st.set_page_config(
    page_title="Game Sales Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 3. DATEN AUS SQLITE LADEN
# ============================================================

# load_data() stammt aus unserer eigenen
# Datei dashboard/data_loader.py.
#
# try:
#   Versucht, die Daten zu laden.
#
# except:
#   Fängt bekannte Datei- und Datenbankfehler ab.

try:

    df = load_data()

except (FileNotFoundError, sqlite3.Error) as error:

    # Fehlermeldung im Browser anzeigen.

    st.error(str(error))

    # Ausführung stoppen.

    st.stop()


# ============================================================
# 4. DATENSATZ ÜBERPRÜFEN
# ============================================================

# empty:
#   Prüft, ob der DataFrame leer ist.

if df.empty:

    st.warning("Die Datenbank enthält keine Spiele.")

    st.stop()


# Wir definieren die benötigten Spalten.
#
# set:
#   Eine Menge aus eindeutigen Elementen.
#
# Durch die Mengendifferenz finden wir heraus,
# ob eine benötigte Spalte fehlt.

required_columns = {
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "Global_Sales",
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales"
}

missing_columns = required_columns - set(df.columns)

if missing_columns:

    st.error(
        f"Folgende Spalten fehlen: {sorted(missing_columns)}"
    )

    st.stop()


# ============================================================
# 5. DASHBOARD-ÜBERSCHRIFT
# ============================================================

# Hauptüberschrift anzeigen.

st.title("🎮 Game Sales Analytics")

# Beschreibung der Anwendung.

st.write(
    "Interaktives Dashboard zur Analyse "
    "historischer Videospiel-Verkaufszahlen."
)

# Horizontale Trennlinie erstellen.

st.divider()


# ============================================================
# 6. FILTER IN DER SEITENLEISTE
# ============================================================

st.sidebar.header("🔎 Datenfilter")


# ============================================================
# 6.1 GENRE-FILTER
# ============================================================

# dropna():
#   Entfernt fehlende Werte.
#
# unique():
#   Liefert alle unterschiedlichen Genres.
#
# tolist():
#   Wandelt die Werte in eine Python-Liste um.
#
# sorted():
#   Sortiert die Liste alphabetisch.
#
# "Alle":
#   Zeigt alle Genres ohne Einschränkung.

genre_options = ["Alle"] + sorted(
    df["Genre"].dropna().unique().tolist()
)

# Dropdown-Menü für die Genreauswahl erstellen.

selected_genre = st.sidebar.selectbox(
    "Genre auswählen",
    genre_options
)


# ============================================================
# 6.2 PLATTFORM-FILTER
# ============================================================

# Liste aller Plattformen erstellen.

platform_options = ["Alle"] + sorted(
    df["Platform"].dropna().unique().tolist()
)

# Dropdown-Menü für die Plattformauswahl.

selected_platform = st.sidebar.selectbox(
    "Plattform auswählen",
    platform_options
)


# ============================================================
# 6.3 ZEITRAUMFILTER
# ============================================================

# dropna():
#   Entfernt fehlende Jahreszahlen.
#
# min():
#   Ermittelt das kleinste Erscheinungsjahr.
#
# max():
#   Ermittelt das größte Erscheinungsjahr.
#
# int():
#   Wandelt die Werte in Ganzzahlen um.

available_years = df["Year"].dropna()

# Prüfen, ob gültige Jahreszahlen existieren.

if available_years.empty:

    st.error("Keine gültigen Erscheinungsjahre vorhanden.")

    st.stop()

min_year = int(available_years.min())

max_year = int(available_years.max())


# st.sidebar.slider():
#   Erstellt einen Zeitraum-Schieberegler.
#
# Da value ein Tupel aus zwei Zahlen ist,
# können Startjahr und Endjahr gewählt werden.
#
# Beispiel:
#   selected_years = (2000, 2010)

selected_years = st.sidebar.slider(
    "Erscheinungsjahre auswählen",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)


# ============================================================
# 7. DATEN FILTERN
# ============================================================

# copy():
#   Erstellt eine unabhängige Kopie.
#
# Der ursprüngliche DataFrame bleibt erhalten.

filtered_df = df.copy()


# ============================================================
# 7.1 ZEITRAUMFILTER
# ============================================================

# between():
#   Prüft, ob ein Jahr innerhalb des
#   gewählten Zeitraums liegt.
#
# Beide Jahresgrenzen werden eingeschlossen.

filtered_df = filtered_df[
    filtered_df["Year"].between(
        selected_years[0],
        selected_years[1]
    )
]


# ============================================================
# 7.2 GENRE-FILTER
# ============================================================

# Wenn der Benutzer ein bestimmtes Genre wählt,
# filtern wir den DataFrame entsprechend.

if selected_genre != "Alle":

    filtered_df = filtered_df[
        filtered_df["Genre"] == selected_genre
    ]


# ============================================================
# 7.3 PLATTFORM-FILTER
# ============================================================

# Wenn eine Plattform ausgewählt wurde,
# berücksichtigen wir nur deren Spiele.

if selected_platform != "Alle":

    filtered_df = filtered_df[
        filtered_df["Platform"] == selected_platform
    ]


# ============================================================
# 7.4 LEERE FILTERERGEBNISSE
# ============================================================

# Manche Kombinationen liefern keine Treffer.
#
# empty:
#   Prüft, ob der DataFrame leer ist.

if filtered_df.empty:

    st.warning(
        "Für diese Filterkombination "
        "wurden keine Spiele gefunden."
    )

    st.stop()


# ============================================================
# 8. KENNZAHLEN BERECHNEN
# ============================================================

# len():
#   Anzahl der Spieleinträge.

total_games = len(filtered_df)

# sum():
#   Addiert die weltweiten Verkaufszahlen.
#
# Einheit: Millionen Exemplare.

total_sales = filtered_df["Global_Sales"].sum()

# nunique():
#   Zählt unterschiedliche Plattformen.

total_platforms = filtered_df["Platform"].nunique()

# Anzahl unterschiedlicher Genres.

total_genres = filtered_df["Genre"].nunique()


# ============================================================
# 9. KENNZAHLEN ANZEIGEN
# ============================================================

# Vier Spalten nebeneinander erstellen.

col1, col2, col3, col4 = st.columns(4)


# Anzahl der Spieleinträge.

with col1:

    st.metric(
        "Spieleinträge",
        f"{total_games:,}"
    )


# Weltweite Gesamtverkäufe.

with col2:

    st.metric(
        "Weltweite Verkäufe (Mio.)",
        f"{total_sales:,.2f}"
    )


# Anzahl der Plattformen.

with col3:

    st.metric(
        "Plattformen",
        total_platforms
    )


# Anzahl der Genres.

with col4:

    st.metric(
        "Genres",
        total_genres
    )


# ============================================================
# 10. VERKÄUFE NACH GENRE
# ============================================================

st.subheader("📊 Weltweite Verkäufe nach Genre")


# groupby():
#   Gruppiert Spiele nach ihrem Genre.
#
# sum():
#   Addiert die Verkaufszahlen jeder Gruppe.
#
# reset_index():
#   Erstellt einen normalen DataFrame.

genre_sales = (
    filtered_df
    .groupby("Genre")["Global_Sales"]
    .sum()
    .reset_index()
)


# Genres nach Verkaufszahlen sortieren.

genre_sales = genre_sales.sort_values(
    by="Global_Sales",
    ascending=False
)


# Interaktives Balkendiagramm erstellen.

fig_genre = px.bar(
    genre_sales,
    x="Genre",
    y="Global_Sales",
    title="Verkäufe pro Genre",
    labels={
        "Genre": "Genre",
        "Global_Sales": "Verkäufe (Mio.)"
    }
)


# Reihenfolge der Genre-Balken festlegen.

fig_genre.update_xaxes(
    categoryorder="array",
    categoryarray=genre_sales["Genre"].tolist()
)


# Diagramm anzeigen.

st.plotly_chart(
    fig_genre,
    width="stretch"
)


# ============================================================
# 11. REGIONALE VERKAUFSZAHLEN
# ============================================================

st.subheader("🌍 Regionale Verkaufszahlen")


# Liste der regionalen Verkaufsspalten.

region_columns = [
    "NA_Sales",
    "EU_Sales",
    "JP_Sales",
    "Other_Sales"
]


# Verkäufe pro Region addieren.
#
# reset_index():
#   Wandelt die Ergebnisse in eine Tabelle um.

regional_sales = (
    filtered_df[region_columns]
    .sum()
    .reset_index()
)


# Spalten verständlich benennen.

regional_sales.columns = [
    "Region",
    "Sales"
]


# Regionsnamen ersetzen.

regional_sales["Region"] = regional_sales[
    "Region"
].replace({
    "NA_Sales": "Nordamerika",
    "EU_Sales": "Europa",
    "JP_Sales": "Japan",
    "Other_Sales": "Andere Regionen"
})


# Donut-Diagramm erstellen.
#
# hole=0.4:
#   Erzeugt das Loch in der Mitte.

fig_region = px.pie(
    regional_sales,
    names="Region",
    values="Sales",
    hole=0.4,
    title="Regionale Verteilung der Verkäufe"
)


# Diagramm anzeigen.

st.plotly_chart(
    fig_region,
    width="stretch"
)


# ============================================================
# 12. TOP 10 SPIELE
# ============================================================

st.subheader("🏆 Top 10 Spiele")


# sort_values():
#   Sortiert nach weltweiten Verkaufszahlen.
#
# ascending=False:
#   Die höchsten Werte stehen zuerst.
#
# head(10):
#   Begrenzt die Auswahl auf zehn Einträge.
#
# copy():
#   Erstellt eine eigenständige Kopie.

top_games = (
    filtered_df
    .sort_values(
        by="Global_Sales",
        ascending=False
    )
    .head(10)
    .copy()
)


# Spielnamen und Plattform kombinieren.
#
# Dadurch unterscheiden wir beispielsweise
# verschiedene Plattformversionen eines Spiels.

top_games["Game_Label"] = (
    top_games["Name"].astype(str)
    + " ("
    + top_games["Platform"].astype(str)
    + ")"
)


# Ein horizontales Balkendiagramm erstellen.
#
# orientation="h":
#   Horizontale Balken.
#
# color:
#   Verkaufszahlen bestimmen die Farbskala.

fig_top_games = px.bar(
    top_games,
    x="Global_Sales",
    y="Game_Label",
    orientation="h",
    color="Global_Sales",
    title="Top 10 Spiele nach weltweiten Verkäufen",
    labels={
        "Global_Sales": "Verkäufe (Mio.)",
        "Game_Label": "Spiel"
    }
)


# Größten Balken oben anzeigen.

fig_top_games.update_yaxes(
    categoryorder="total ascending"
)


# Höhe und Abstände des Diagramms anpassen.

fig_top_games.update_layout(
    height=550,
    margin=dict(l=180, r=20, t=60, b=40)
)


# Diagramm anzeigen.

st.plotly_chart(
    fig_top_games,
    width="stretch"
)


# ============================================================
# 13. VERKÄUFE NACH ERSCHEINUNGSJAHR
# ============================================================

st.subheader("📈 Verkäufe nach Erscheinungsjahr")


# groupby("Year"):
#   Gruppiert alle gefilterten Spiele nach Jahr.
#
# sum():
#   Addiert die Gesamtverkäufe der Spiele,
#   die im jeweiligen Jahr erschienen sind.
#
# reset_index():
#   Erstellt einen normalen DataFrame.
#
# sort_values("Year"):
#   Sortiert die Jahre chronologisch.

yearly_sales = (
    filtered_df
    .groupby("Year")["Global_Sales"]
    .sum()
    .reset_index()
    .sort_values("Year")
)


# Interaktives Liniendiagramm erstellen.

fig_yearly_sales = px.line(
    yearly_sales,
    x="Year",
    y="Global_Sales",
    markers=True,
    title="Verkäufe nach Erscheinungsjahr",
    labels={
        "Year": "Erscheinungsjahr",
        "Global_Sales": "Verkäufe (Mio.)"
    }
)


# Diagramm anzeigen.

st.plotly_chart(
    fig_yearly_sales,
    width="stretch"
)


# Hinweis zur Interpretation:
#
# Die Zeitreihe zeigt Gesamtverkäufe der Spiele,
# gruppiert nach ihrem Erscheinungsjahr.
#
# Es handelt sich nicht um jährliche
# Verkaufstransaktionen.

st.caption(
    "Die Zeitreihe zeigt erfasste Gesamtverkäufe "
    "von Spielen je Erscheinungsjahr, nicht die "
    "tatsächlichen Verkäufe im jeweiligen Kalenderjahr."
)


# ============================================================
# 14. INTERAKTIVE SPIELETABELLE
# ============================================================

st.subheader("📋 Gefilterte Spieledaten")


# Spalten auswählen, die wir anzeigen möchten.

display_columns = [
    "Name",
    "Platform",
    "Year",
    "Genre",
    "Publisher",
    "Global_Sales"
]


# st.dataframe():
#   Erstellt eine interaktive Tabelle.
#
# hide_index=True:
#   Versteckt zusätzliche Pandas-Zeilennummern.

st.dataframe(
    filtered_df[display_columns],
    width="stretch",
    hide_index=True
)


# ============================================================
# 15. CSV-DOWNLOAD
# ============================================================

st.subheader("📥 Daten exportieren")


# to_csv():
#   Wandelt unseren gefilterten DataFrame
#   in eine CSV-Zeichenkette um.
#
# index=False:
#   Verhindert zusätzliche Zeilennummern.
#
# encode("utf-8-sig"):
#   Wandelt den Text in Bytes um.
#
# UTF-8 mit BOM hilft häufig beim
# Öffnen der CSV-Datei in Excel.

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8-sig")


# Einen Download-Button erstellen.

st.download_button(
    label="📥 Gefilterte Daten herunterladen",
    data=csv_data,
    file_name="game_sales_filtered.csv",
    mime="text/csv"
)


# ============================================================
# 16. INFORMATIONEN ZUM DATENSATZ
# ============================================================

# Horizontale Trennlinie.

st.divider()


# Kurze Information zum Datensatz anzeigen.

st.caption(
    "Game Sales Analytics v1.3 | "
    "Historischer Video Game Sales Datensatz | "
    "Verkaufszahlen in Millionen Exemplaren | "
    "Keine aktuellen Verkaufsstatistiken"
)


# ============================================================
# PROGRAMMENDE
# ============================================================
#
# Unser Dashboard kann jetzt:
#
# 1. Daten über einen zentralen Data Loader laden.
# 2. Genres, Plattformen und Jahre filtern.
# 3. Dynamische Kennzahlen darstellen.
# 4. Interaktive Genre-Diagramme anzeigen.
# 5. Regionale Verkäufe vergleichen.
# 6. Top-10-Spiele visualisieren.
# 7. Verkaufszahlen nach Erscheinungsjahr darstellen.
# 8. Eine interaktive Tabelle anzeigen.
# 9. Gefilterte Daten als CSV exportieren.
#
# Nächster Schritt:
#   Dashboard in mehrere Seiten aufteilen.
#
# ============================================================
