# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### How real-world recommenders work

Platforms like Spotify and YouTube combine several kinds of signals.
**Collaborative filtering** learns from the behavior of many users (plays,
skips, saves, playlists): people with similar histories are assumed to like
similar songs. **Content-based filtering** compares the attributes of the
songs themselves (genre, mood, tempo, energy) to what one user has liked.
Spotify also uses language and audio models so brand-new songs with no
listening history can still be recommended. YouTube describes a two-stage
design: a first model narrows millions of videos to a few hundred
candidates, then a second model ranks those candidates.

### What my version does

My simulator is **purely content-based**. It has no data about other
listeners, only a catalog of song attributes and one user's taste profile.

- **Input data:** the song catalog (`data/songs.csv`).
- **User preferences:** a taste profile with target values.
- **Ranking:** every song gets a score, then the list is sorted and the
  top k are returned with reasons.

### Features used

- **Song:** `genre`, `mood`, `energy` (0-1), `danceability` (0-1).
  (`title`, `artist` and `id` are only for display.)
- **UserProfile:** `favorite_genre`, `favorite_mood`, `target_energy`,
  `target_danceability`.

### Algorithm recipe (draft)

Scoring rule (one song):

| Feature | Rule | Max points |
|---|---|---|
| genre | exact match | 2.0 |
| mood | exact match | 1.0 |
| energy | 1.5 x (1 - abs(song - target)) | 1.5 |
| danceability | 1.0 x (1 - abs(song - target)) | 1.0 |

Ranking rule (all songs): score every song, sort from highest to lowest,
return the top k.

Closeness matters more than "higher is better": if a user wants energy 0.8,
a 0.82 song should beat a 0.93 song.

### Expected biases

- Genre is worth the most points, so a great mood and energy match in a
  different genre can lose to a weaker song with the right genre label.
- Genre is an exact match, so "indie pop" gets nothing for a "pop" fan.
- With a small catalog, genres with only one or two songs will fill the
  top results with filler once they run out.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



