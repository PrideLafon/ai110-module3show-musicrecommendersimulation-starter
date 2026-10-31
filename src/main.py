"""Command line runner for the Music Recommender Simulation."""

from tabulate import tabulate
from typing import Dict, List

from src.recommender import load_songs, recommend_songs

PROFILES: Dict[str, Dict] = {
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy",
        "energy": 0.85, "danceability": 0.85,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "chill",
        "energy": 0.38, "danceability": 0.60,
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense",
        "energy": 0.92, "danceability": 0.60,
    },
    "ADVERSARIAL: Sad But Hyper": {
        "genre": "pop", "mood": "sad",
        "energy": 0.90, "danceability": 0.50,
    },
    "ADVERSARIAL: Unknown Genre": {
        "genre": "k-pop", "mood": "happy",
        "energy": 0.88, "danceability": 0.85,
    },
}


def show_recommendations(
    name: str, user_prefs: Dict, songs: List[Dict], k: int = 5
) -> None:
    """Print the top k recommendations for one profile as a table."""
    print(f"\n=== Profile: {name} ===")
    print(f"Preferences: {user_prefs}\n")
    results = recommend_songs(user_prefs, songs, k=k)
    rows = []
    for rank, (song, score, explanation) in enumerate(results, start=1):
        reasons = "\n".join(f"- {r}" for r in explanation.split("; "))
        rows.append([
            rank,
            song["title"],
            song["artist"],
            f"{song['genre']} / {song['mood']}",
            f"{score:.2f}",
            reasons,
        ])
    headers = ["#", "Title", "Artist", "Genre / Mood", "Score", "Why"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def main() -> None:
    """Load the catalog and print recommendations for each profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for name, prefs in PROFILES.items():
        show_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()