import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: Optional[List[str]] = None
    language: str = "english"
    instrumentalness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file as dictionaries with typed values."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row["popularity"]),
                "release_decade": int(row["release_decade"]),
                "mood_tags": row["mood_tags"].split("|"),
                "language": row["language"],
                "instrumentalness": float(row["instrumentalness"]),
            })
    return songs

WEIGHTS = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 1.5,
    "danceability": 1.0,
}


def closeness(value: float, target: float) -> float:
    """Return similarity: 1.0 if identical, falling to 0.0 if far apart."""
    return max(0.0, 1.0 - abs(value - target))


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += WEIGHTS["genre"]
        reasons.append(
            f"genre match: {song['genre']} (+{WEIGHTS['genre']:.2f})"
        )
    if song["mood"] == user_prefs.get("mood"):
        score += WEIGHTS["mood"]
        reasons.append(
            f"mood match: {song['mood']} (+{WEIGHTS['mood']:.2f})"
        )

    for feature in ("energy", "danceability"):
        if feature not in user_prefs:
            continue
        similarity = closeness(song[feature], user_prefs[feature])
        points = WEIGHTS[feature] * similarity
        score += points
        reasons.append(
            f"{feature} {song[feature]} vs target "
            f"{user_prefs[feature]} (+{points:.2f})"
        )

    return round(score, 4), reasons

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Rank all songs for a user and return the top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["id"]))
    return ranked[:k]
