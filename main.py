import pandas as pd 
import matplotlib.pyplot as plt

df = pd.read_csv("C:/Users/Kolbi/IdeaProjects/game-sales-analysis/data/vgsales.csv")

genre_count = df["Genre"].value_counts()


plt.figure(figsize=(12, 6))

plt.bar(genre_count.index, genre_count.values)
plt.title("Anzahl der Spiele pro Genre")
plt.xlabel("Genre")
plt.ylabel("Anzahl der Spiele")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.show()


