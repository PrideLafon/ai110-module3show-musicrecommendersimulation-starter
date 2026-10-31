import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass

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
    target_danceability: Optional[float] = None

    def to_prefs(self) -> Dict:
        """Convert the profile to the dict format score_song expects."""
        prefs = {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
        }
        if self.target_danceability is not None:
            prefs["danceability"] = self.target_danceability
        return prefs

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user."""
        by_id = {song.id: song for song in self.songs}
        ranked = recommend_songs(
            user.to_prefs(), [asdict(s) for s in self.songs], k=k
        )
        return [by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain in text why this song fits this user."""
        _, reasons = score_song(user.to_prefs(), asdict(song))
        return "; ".join(reasons) or "weak match: no overlap"

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

MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 2.0, "mood": 1.0, "energy": 1.5, "danceability": 1.0,
    },
    "genre_first": {
        "genre": 4.0, "mood": 1.0, "energy": 1.0, "danceability": 0.5,
    },
    "mood_first": {
        "genre": 1.0, "mood": 3.0, "energy": 1.0, "danceability": 1.0,
    },
    "energy_focused": {
        "genre": 1.0, "mood": 1.0, "energy": 3.0, "danceability": 1.0,
    },
}
DEFAULT_MODE = "balanced"


def get_weights(mode: str) -> Dict[str, float]:
    """Return the weight set (the strategy) for a ranking mode."""
    if mode not in MODES:
        raise ValueError(
            f"Unknown mode '{mode}'. Choose from: {', '.join(MODES)}"
        )
    return MODES[mode]


def closeness(value: float, target: float) -> float:
    """Return similarity: 1.0 if identical, falling to 0.0 if far apart."""
    return max(0.0, 1.0 - abs(value - target))


def score_song(
    user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE
) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (score, reasons)."""
    weights = get_weights(mode)
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += weights["genre"]
        reasons.append(
            f"genre match: {song['genre']} (+{weights['genre']:.2f})"
        )
    if song["mood"] == user_prefs.get("mood"):
        score += weights["mood"]
        reasons.append(
            f"mood match: {song['mood']} (+{weights['mood']:.2f})"
        )

    for feature in ("energy", "danceability"):
        if feature not in user_prefs:
            continue
        similarity = closeness(song[feature], user_prefs[feature])
        points = weights[feature] * similarity
        score += points
        reasons.append(
            f"{feature} {song[feature]} vs target "
            f"{user_prefs[feature]} (+{points:.2f})"
        )

    return round(score, 4), reasons


ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5


def diversity_penalty(
    song: Dict, chosen: List[Tuple[Dict, float, List[str]]]
) -> Tuple[float, List[str]]:
    """Return a penalty (and reasons) for repeating an artist or genre."""
    artist_repeats = sum(1 for s, _, _ in chosen
                         if s["artist"] == song["artist"])
    genre_repeats = sum(1 for s, _, _ in chosen
                        if s["genre"] == song["genre"])
    penalty = 0.0
    reasons = []
    if artist_repeats:
        amount = ARTIST_PENALTY * artist_repeats
        penalty += amount
        reasons.append(f"diversity: artist already listed (-{amount:.2f})")
    if genre_repeats:
        amount = GENRE_PENALTY * genre_repeats
        penalty += amount
        reasons.append(f"diversity: genre already listed (-{amount:.2f})")
    return penalty, reasons


def pick_diverse(
    scored: List[Tuple[Dict, float, List[str]]], k: int
) -> List[Tuple[Dict, float, List[str]]]:
    """Pick k songs one at a time, penalizing repeated artists/genres."""
    pool = list(scored)
    chosen = []
    while pool and len(chosen) < k:
        options = []
        for song, base_score, reasons in pool:
            penalty, extra = diversity_penalty(song, chosen)
            options.append((base_score - penalty, song, reasons + extra))
        best = max(options, key=lambda o: (o[0], -o[1]["id"]))
        chosen.append((best[1], round(best[0], 4), best[2]))
        pool = [item for item in pool if item[0]["id"] != best[1]["id"]]
    return chosen


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5,
    mode: str = DEFAULT_MODE, diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Rank all songs for a user and return the top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, reasons))

    ranked = sorted(scored, key=lambda item: (-item[1], item[0]["id"]))
    top = pick_diverse(ranked, k) if diversity else ranked[:k]
    return [(song, score, "; ".join(why)) for song, score, why in top]