"""Core logic for the Music Recommender Simulation.

Pipeline: load_songs -> score_song (one song) -> recommend_songs (all).
Scoring is content-based: it compares song attributes to one listener's
stated preferences. It never uses other listeners' behavior.
"""

import csv
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Song:
    """A song and its attributes."""

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
    mood_tags: List[str] = field(default_factory=list)
    language: str = "english"
    instrumentalness: float = 0.0


@dataclass
class UserProfile:
    """A listener's taste. Optional targets are skipped when left None."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_danceability: Optional[float] = None
    target_popularity: Optional[int] = None
    preferred_decade: Optional[int] = None
    preferred_language: Optional[str] = None
    preferred_mood_tags: List[str] = field(default_factory=list)
    prefers_instrumental: Optional[bool] = None

    def to_prefs(self) -> Dict:
        """Convert the profile to the dict format score_song expects."""
        prefs = {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
            "danceability": self.target_danceability,
            "popularity": self.target_popularity,
            "release_decade": self.preferred_decade,
            "language": self.preferred_language,
            "mood_tags": self.preferred_mood_tags,
            "prefers_instrumental": self.prefers_instrumental,
        }
        return {k: v for k, v in prefs.items() if v is not None and v != []}


class Recommender:
    """Object-oriented wrapper around the functional pipeline below."""

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


# ---------------------------------------------------------------------
# Ranking modes (Strategy pattern): a mode is just a set of weights.
# CORE features are always scored. EXTRA features are only scored when
# the listener's profile gives a preference for them.
# ---------------------------------------------------------------------

EXTRA_WEIGHTS = {
    "acousticness": 0.5, "instrumentalness": 0.5, "popularity": 0.25,
    "release_decade": 0.25, "mood_tags": 0.5, "language": 0.5,
}


def _mode(genre: float, mood: float, energy: float, dance: float) -> Dict:
    """Build a full weight set from the four core weights."""
    core = {"genre": genre, "mood": mood,
            "energy": energy, "danceability": dance}
    return {**core, **EXTRA_WEIGHTS}


MODES: Dict[str, Dict[str, float]] = {
    "balanced": _mode(genre=2.0, mood=1.0, energy=1.5, dance=1.0),
    "genre_first": _mode(genre=4.0, mood=1.0, energy=1.0, dance=0.5),
    "mood_first": _mode(genre=1.0, mood=3.0, energy=1.0, dance=1.0),
    "energy_focused": _mode(genre=1.0, mood=1.0, energy=3.0, dance=1.0),
}
DEFAULT_MODE = "balanced"

# Numeric preference -> (scale, label). Scale = gap that scores zero.
NUMERIC_FEATURES = {
    "energy": (1.0, "energy"),
    "danceability": (1.0, "danceability"),
    "popularity": (100.0, "popularity"),
    "release_decade": (30.0, "decade"),
}


def get_weights(mode: str) -> Dict[str, float]:
    """Return the weight set (the strategy) for a ranking mode."""
    if mode not in MODES:
        raise ValueError(
            f"Unknown mode '{mode}'. Choose from: {', '.join(MODES)}"
        )
    return MODES[mode]


def closeness(value: float, target: float, scale: float = 1.0) -> float:
    """Return similarity: 1.0 if identical, 0.0 if 'scale' apart."""
    return max(0.0, 1.0 - abs(value - target) / scale)


def _score_labels(prefs: Dict, song: Dict, w: Dict) -> List[tuple]:
    """Score the exact-match labels: genre, mood and language."""
    parts = []
    if song["genre"] == prefs.get("genre"):
        parts.append((w["genre"], f"genre match: {song['genre']}"))
    if song["mood"] == prefs.get("mood"):
        parts.append((w["mood"], f"mood match: {song['mood']}"))
    if "language" in prefs and song.get("language") == prefs["language"]:
        parts.append((w["language"], f"language match: {song['language']}"))
    return parts


def _score_numbers(prefs: Dict, song: Dict, w: Dict) -> List[tuple]:
    """Score numeric features: closer to the target earns more."""
    parts = []
    for feature, (scale, label) in NUMERIC_FEATURES.items():
        if feature not in prefs:
            continue
        similarity = closeness(song[feature], prefs[feature], scale)
        reason = f"{label} {song[feature]} vs target {prefs[feature]}"
        parts.append((w[feature] * similarity, reason))
    return parts


def _score_extras(prefs: Dict, song: Dict, w: Dict) -> List[tuple]:
    """Score acousticness, instrumentalness and mood-tag overlap."""
    parts = []
    if "likes_acoustic" in prefs:
        value = song["acousticness"]
        similarity = value if prefs["likes_acoustic"] else 1.0 - value
        parts.append((w["acousticness"] * similarity,
                      f"acousticness {value}"))
    if "prefers_instrumental" in prefs:
        value = song["instrumentalness"]
        similarity = value if prefs["prefers_instrumental"] else 1.0 - value
        parts.append((w["instrumentalness"] * similarity,
                      f"instrumentalness {value}"))
    wanted = set(prefs.get("mood_tags", []))
    shared = wanted & set(song.get("mood_tags", []))
    if shared:
        parts.append((w["mood_tags"] * len(shared) / len(wanted),
                      "mood tags: " + ", ".join(sorted(shared))))
    return parts


def score_song(
    user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE
) -> Tuple[float, List[str]]:
    """Score one song against user preferences; return (score, reasons)."""
    weights = get_weights(mode)
    labels = _score_labels(user_prefs, song, weights)
    parts = (labels[:2] + _score_numbers(user_prefs, song, weights)
             + labels[2:] + _score_extras(user_prefs, song, weights))
    parts = [(points, why) for points, why in parts if points > 0]
    score = round(sum(points for points, _ in parts), 4)
    reasons = [f"{why} (+{points:.2f})" for points, why in parts]
    return score, reasons


# ---------------------------------------------------------------------
# Diversity re-ranking (stretch feature)
# ---------------------------------------------------------------------

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