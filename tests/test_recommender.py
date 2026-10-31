from pathlib import Path

import pytest

from src.recommender import (MODES, Recommender, Song, UserProfile,
                             load_songs, recommend_songs, score_song)

DATA = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


def make_small_recommender() -> Recommender:
    songs = [
        Song(id=1, title="Test Pop Track", artist="Test Artist",
             genre="pop", mood="happy", energy=0.8, tempo_bpm=120,
             valence=0.9, danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="Test Artist",
             genre="lofi", mood="chill", energy=0.4, tempo_bpm=80,
             valence=0.6, danceability=0.5, acousticness=0.9),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    results = make_small_recommender().recommend(user, k=2)
    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_best_match_ranks_first_even_if_listed_last():
    rec = make_small_recommender()
    rec.songs.reverse()  # the lofi song is now listed first
    user = UserProfile("pop", "happy", 0.8, False)
    assert rec.recommend(user, k=1)[0].title == "Test Pop Track"


def test_score_song_follows_the_recipe():
    song = {"genre": "pop", "mood": "happy",
            "energy": 0.8, "danceability": 0.8}
    score, reasons = score_song(dict(song), song)
    assert score == 5.5  # 2.0 + 1.0 + 1.5 + 1.0
    assert len(reasons) == 4


def test_recommend_songs_returns_sorted_top_k():
    songs = load_songs(str(DATA))
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    results = recommend_songs(prefs, songs, k=3)
    scores = [score for _, score, _ in results]
    assert len(results) == 3
    assert scores == sorted(scores, reverse=True)
    assert results[0][0]["title"] == "Sunrise City"


def test_different_profiles_get_different_top_songs():
    songs = load_songs(str(DATA))
    pop = {"genre": "pop", "mood": "happy", "energy": 0.85}
    lofi = {"genre": "lofi", "mood": "chill", "energy": 0.38}
    assert recommend_songs(pop, songs, 1)[0][0]["genre"] == "pop"
    assert recommend_songs(lofi, songs, 1)[0][0]["genre"] == "lofi"


def test_ranking_modes_change_the_order():
    songs = load_songs(str(DATA))
    pop = {"genre": "pop", "mood": "happy",
           "energy": 0.85, "danceability": 0.85}
    orders = {
        mode: [s["id"] for s, _, _ in recommend_songs(pop, songs, 5, mode)]
        for mode in MODES
    }
    assert len({tuple(order) for order in orders.values()}) > 1


def test_unknown_mode_raises_clear_error():
    songs = load_songs(str(DATA))
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop"}, songs, k=3, mode="nope")


LOFI = {"genre": "lofi", "mood": "chill",
        "energy": 0.38, "danceability": 0.60}


def test_diversity_pushes_down_a_repeated_artist():
    songs = load_songs(str(DATA))
    plain = [s["title"] for s, _, _ in recommend_songs(LOFI, songs, 5)]
    diverse = [
        s["title"]
        for s, _, _ in recommend_songs(LOFI, songs, 5, diversity=True)
    ]
    assert plain[0] == diverse[0]  # the best match is never penalized
    assert diverse.index("Focus Flow") > plain.index("Focus Flow")


def test_diversity_explains_its_penalty():
    songs = load_songs(str(DATA))
    results = recommend_songs(LOFI, songs, 5, diversity=True)
    focus = [why for s, _, why in results if s["title"] == "Focus Flow"][0]
    assert "diversity: artist already listed" in focus