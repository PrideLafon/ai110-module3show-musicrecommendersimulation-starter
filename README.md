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

- **Genre outweighs everything else.** Genre is worth up to 2.0 points, so
  in a hand-run test a slow, sad pop song (energy 0.45) ranked #3 for a
  happy, high-energy pop fan, above a happy afrobeats song with almost
  exactly the right energy, only because its genre label said "pop".
- **Exact-match genre is blunt.** "Indie pop" earns nothing for a "pop" fan.
- **Small catalog.** Rock has only two songs, so after those two, the top
  results fill with songs that match only on mood or energy.
- **Danceability adds little here.** In a hand-run test it separated
  chill lofi from intense rock by only about 0.04 points; energy did the
  work. I plan to test removing it.

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
=== Profile: Default Pop/Happy ===
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}

1. Sunrise City by Neon Echo [pop / happy]
   Score: 4.47
   - genre match: pop (+2.00)
   - mood match: happy (+1.00)
   - energy 0.82 vs target 0.8 (+1.47)

2. Gym Hero by Max Pulse [pop / intense]
   Score: 3.31
   - genre match: pop (+2.00)
   - energy 0.93 vs target 0.8 (+1.30)

3. Soleil de Minuit by Camille Aubry [pop / sad]
   Score: 2.98
   - genre match: pop (+2.00)
   - energy 0.45 vs target 0.8 (+0.97)

4. Golden Hour Groove by Zuri Kante [afrobeats / happy]
   Score: 2.50
   - mood match: happy (+1.00)
   - energy 0.8 vs target 0.8 (+1.50)

5. Rooftop Lights by Indigo Parade [indie pop / happy]
   Score: 2.44
   - mood match: happy (+1.00)
   - energy 0.76 vs target 0.8 (+1.44)
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



