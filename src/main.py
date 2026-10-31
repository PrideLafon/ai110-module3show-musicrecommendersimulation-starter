"""Command line runner for the Music Recommender Simulation."""

import argparse
from typing import Dict, List

from tabulate import tabulate

from src.recommender import DEFAULT_MODE, MODES, load_songs, recommend_songs

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
    name: str, user_prefs: Dict, songs: List[Dict],
    mode: str = DEFAULT_MODE, diversity: bool = False, k: int = 5,
) -> None:
    """Print the top k recommendations for one profile as a table."""
    tag = " + diversity" if diversity else ""
    print(f"\n=== Profile: {name} | mode: {mode}{tag} ===")
    print(f"Preferences: {user_prefs}\n")
    results = recommend_songs(
        user_prefs, songs, k=k, mode=mode, diversity=diversity
    )
    rows = []
    for rank, (song, score, explanation) in enumerate(results, start=1):
        reasons = "\n".join(f"- {r}" for r in explanation.split("; "))
        rows.append([
            rank, song["title"], song["artist"],
            f"{song['genre']} / {song['mood']}", score, reasons,
        ])
    headers = ["#", "Title", "Artist", "Genre / Mood", "Score", "Why"]
    print(tabulate(rows, headers=headers, tablefmt="grid", floatfmt=".2f"))


def compare_modes(
    name: str, user_prefs: Dict, songs: List[Dict], k: int = 5
) -> None:
    """Print each mode's top k side by side for one profile."""
    print(f"\n=== Mode comparison: {name} ===")
    columns = {}
    for mode in MODES:
        top = recommend_songs(user_prefs, songs, k=k, mode=mode)
        columns[mode] = [f"{s['title']} ({sc:.2f})" for s, sc, _ in top]
    rows = [
        [rank + 1] + [columns[mode][rank] for mode in MODES]
        for rank in range(k)
    ]
    print(tabulate(rows, headers=["#"] + list(MODES), tablefmt="grid"))


def build_parser() -> argparse.ArgumentParser:
    """Define the command line options."""
    parser = argparse.ArgumentParser(description="Music recommender")
    parser.add_argument(
        "--mode", choices=list(MODES), default=DEFAULT_MODE,
        help="ranking mode (default: balanced)",
    )
    parser.add_argument(
        "--diversity", action="store_true",
        help="penalize repeated artists and genres in the top results",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="show every ranking mode side by side",
    )
    return parser


def main() -> None:
    """Load the catalog and print recommendations for each profile."""
    args = build_parser().parse_args()
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for name, prefs in PROFILES.items():
        if args.compare:
            compare_modes(name, prefs, songs)
        else:
            show_recommendations(
                name, prefs, songs, mode=args.mode, diversity=args.diversity
            )


if __name__ == "__main__":
    main()