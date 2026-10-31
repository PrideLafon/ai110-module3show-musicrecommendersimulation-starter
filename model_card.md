## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests songs from a small catalog for one listener at a time. It
assumes the listener can describe their taste with a favorite genre, a favorite
mood, and target energy and danceability levels. It is for classroom
exploration of how recommenders work, not for real users or real products.

**Not intended for:** recommending music to real people at scale, judging a
person's taste, or any decision that matters. It is not a model of any real
platform.

---

## 3. How the Model Works

The recommender gives every song a score for one listener, then shows the
songs with the highest scores.

A listener is described by a few target values: a favorite genre, a favorite
mood, and how energetic (0 to 1) and danceable (0 to 1) they want their music
to be. For each song, the system adds up points:

- **Genre:** 2.0 points if the song's genre is exactly the listener's genre.
- **Mood:** 1.0 point if the mood matches exactly.
- **Energy:** up to 1.5 points. A song gets all 1.5 if its energy is exactly
  the target, and fewer points the further away it is, in either direction.
- **Danceability:** up to 1.0 point, scored the same "closer is better" way.

Then the songs are sorted from highest to lowest score and the top few are
returned, each with a short list of reasons showing where its points came
from. This is content-based filtering: it only looks at song attributes and
the listener's targets, never at what other listeners do.

Changes from the starter: the starter code was empty, so everything here is
new. The scoring recipe is genre 2.0, mood 1.0, energy 1.5, danceability 1.0.
The profile also has a "likes acoustic" setting, but this version does not
score it yet.
---

## 4. Data

The catalog has 24 songs and 15 columns, stored in `data/songs.csv`. The first
10 songs came with the starter project, and I added 14 more to cover genres the
starter lacked (hip-hop, EDM, R&B, classical, country, reggae, metal, folk,
afrobeats, Latin, blues, a French-language pop song, and a second rock song).
The data is synthetic: the titles and artists are made up, and the numbers
(energy, danceability and so on) were chosen to be plausible for each genre,
not measured from real audio.

The catalog has 18 genres, but it is uneven: pop and lofi have 3 songs each,
rock and hip-hop have 2, and the other 14 genres have 1. The recommender
scores only genre, mood, energy and danceability. Tempo, valence, acousticness,
popularity, release decade, mood tags, language and instrumentalness are in the
file but not used in the score yet. Missing from the data: lyrics, artist
popularity over time, and any listening history.

---

## 5. Strengths

- It separates very different listeners well. Pop and lofi share no songs in
  their top 5, and lofi and rock share none either. Pop and rock overlap on
  only two songs, Gym Hero and Sunrise City, both high-energy pop tracks.
- Results usually match intuition at #1: Sunrise City for pop, Library Rain for
  lofi, and Storm Runner for rock.
- Every recommendation comes with reasons that add up exactly to its score, so
  it is easy to see why a song ranked where it did.
- It does not crash on odd input. An unknown genre simply earns no genre points.

---

## 6. Limitations and Bias

The system over-weights genre labels and under-penalizes big energy gaps. In my
"Sad But Hyper" test (pop, sad, energy 0.90), the slow sad pop song Soleil de
Minuit (energy 0.45) ranked first. It earned 3.0 points from genre and mood and
still got 0.83 of 1.50 energy points despite being far off the target, because
the closeness rule is linear. The catalog also has only two rock songs, so the
rock listener's list falls from 5.42 at #2 to 3.21 at #3, where the first
non-rock song appears. As a result, listeners who like big genres get better
lists than listeners who like small ones.

---

### Diversity penalty (stretch feature)

With `--diversity`, the system picks songs one at a time and subtracts points
from a song if its artist (-1.00 each) or genre (-0.50 each) is already in
the list. The best match is never penalized, and each penalty is shown in the
reasons column.

How it helps fairness: without it, a catalog with several songs by one
artist can fill the top results with near-copies. For the Chill Lofi listener,
the second LoRoom song (Focus Flow) fell from #3 to #4 and Spacewalk Thoughts
(a different artist and genre) moved up. For the pop listener, the sad song
Soleil de Minuit fell from #3 to #5, below two happy songs.

Trade-offs I noticed: the genre penalty also hurts listeners who really do
want one genre. The Deep Intense Rock profile lost 0.50 points on its second
rock song just for being rock. The penalty is also soft, so Focus Flow still
stayed in the lofi top 5, because the catalog has few lofi alternatives. A
smaller genre penalty or an artist-only penalty would be a fairer default.

## 7. Evaluation

I tested five profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and two
adversarial ones: "Sad But Hyper" (conflicting mood and energy) and "Unknown
Genre" (a genre not in the catalog).

```
Loaded songs: 24

=== Profile: High-Energy Pop ===
Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.85, 'danceability': 0.85}

1. Sunrise City by Neon Echo [pop / happy]
   Score: 5.39
   - genre match: pop (+2.00)
   - mood match: happy (+1.00)
   - energy 0.82 vs target 0.85 (+1.46)
   - danceability 0.79 vs target 0.85 (+0.94)

2. Gym Hero by Max Pulse [pop / intense]
   Score: 4.35
   - genre match: pop (+2.00)
   - energy 0.93 vs target 0.85 (+1.38)
   - danceability 0.88 vs target 0.85 (+0.97)

3. Soleil de Minuit by Camille Aubry [pop / sad]
   Score: 3.57
   - genre match: pop (+2.00)
   - energy 0.45 vs target 0.85 (+0.90)
   - danceability 0.52 vs target 0.85 (+0.67)

4. Golden Hour Groove by Zuri Kante [afrobeats / happy]
   Score: 3.38
   - mood match: happy (+1.00)
   - energy 0.8 vs target 0.85 (+1.43)
   - danceability 0.9 vs target 0.85 (+0.95)

5. Rooftop Lights by Indigo Parade [indie pop / happy]
   Score: 3.33
   - mood match: happy (+1.00)
   - energy 0.76 vs target 0.85 (+1.36)
   - danceability 0.82 vs target 0.85 (+0.97)


=== Profile: Chill Lofi ===
Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.38, 'danceability': 0.6}

1. Library Rain by Paper Lanterns [lofi / chill]
   Score: 5.43
   - genre match: lofi (+2.00)
   - mood match: chill (+1.00)
   - energy 0.35 vs target 0.38 (+1.46)
   - danceability 0.58 vs target 0.6 (+0.98)

2. Midnight Coding by LoRoom [lofi / chill]
   Score: 5.42
   - genre match: lofi (+2.00)
   - mood match: chill (+1.00)
   - energy 0.42 vs target 0.38 (+1.44)
   - danceability 0.62 vs target 0.6 (+0.98)

3. Focus Flow by LoRoom [lofi / focused]
   Score: 4.47
   - genre match: lofi (+2.00)
   - energy 0.4 vs target 0.38 (+1.47)
   - danceability 0.6 vs target 0.6 (+1.00)

4. Spacewalk Thoughts by Orbit Bloom [ambient / chill]
   Score: 3.16
   - mood match: chill (+1.00)
   - energy 0.28 vs target 0.38 (+1.35)
   - danceability 0.41 vs target 0.6 (+0.81)

5. Coffee Shop Stories by Slow Stereo [jazz / relaxed]
   Score: 2.42
   - energy 0.37 vs target 0.38 (+1.48)
   - danceability 0.54 vs target 0.6 (+0.94)


=== Profile: Deep Intense Rock ===
Preferences: {'genre': 'rock', 'mood': 'intense', 'energy': 0.92, 'danceability': 0.6}

1. Storm Runner by Voltline [rock / intense]
   Score: 5.42
   - genre match: rock (+2.00)
   - mood match: intense (+1.00)
   - energy 0.91 vs target 0.92 (+1.48)
   - danceability 0.66 vs target 0.6 (+0.94)

2. Gravel and Gasoline by Dust Engine [rock / intense]
   Score: 5.42
   - genre match: rock (+2.00)
   - mood match: intense (+1.00)
   - energy 0.88 vs target 0.92 (+1.44)
   - danceability 0.58 vs target 0.6 (+0.98)

3. Gym Hero by Max Pulse [pop / intense]
   Score: 3.21
   - mood match: intense (+1.00)
   - energy 0.93 vs target 0.92 (+1.48)
   - danceability 0.88 vs target 0.6 (+0.72)

4. Iron Requiem by Black Anvil [metal / aggressive]
   Score: 2.27
   - energy 0.97 vs target 0.92 (+1.43)
   - danceability 0.45 vs target 0.6 (+0.85)

5. Sunrise City by Neon Echo [pop / happy]
   Score: 2.16
   - energy 0.82 vs target 0.92 (+1.35)
   - danceability 0.79 vs target 0.6 (+0.81)


=== Profile: ADVERSARIAL: Sad But Hyper ===
Preferences: {'genre': 'pop', 'mood': 'sad', 'energy': 0.9, 'danceability': 0.5}

1. Soleil de Minuit by Camille Aubry [pop / sad]
   Score: 4.80
   - genre match: pop (+2.00)
   - mood match: sad (+1.00)
   - energy 0.45 vs target 0.9 (+0.83)
   - danceability 0.52 vs target 0.5 (+0.98)

2. Sunrise City by Neon Echo [pop / happy]
   Score: 4.09
   - genre match: pop (+2.00)
   - energy 0.82 vs target 0.9 (+1.38)
   - danceability 0.79 vs target 0.5 (+0.71)

3. Gym Hero by Max Pulse [pop / intense]
   Score: 4.08
   - genre match: pop (+2.00)
   - energy 0.93 vs target 0.9 (+1.46)
   - danceability 0.88 vs target 0.5 (+0.62)

4. Blue Smoke Lullaby by Old Mill Trio [blues / sad]
   Score: 2.62
   - mood match: sad (+1.00)
   - energy 0.35 vs target 0.9 (+0.67)
   - danceability 0.45 vs target 0.5 (+0.95)

5. Willow Creek Letters by Hollow Pines [folk / sad]
   Score: 2.58
   - mood match: sad (+1.00)
   - energy 0.3 vs target 0.9 (+0.60)
   - danceability 0.48 vs target 0.5 (+0.98)


=== Profile: ADVERSARIAL: Unknown Genre ===
Preferences: {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.88, 'danceability': 0.85}

1. Sunrise City by Neon Echo [pop / happy]
   Score: 3.35
   - mood match: happy (+1.00)
   - energy 0.82 vs target 0.88 (+1.41)
   - danceability 0.79 vs target 0.85 (+0.94)

2. Golden Hour Groove by Zuri Kante [afrobeats / happy]
   Score: 3.33
   - mood match: happy (+1.00)
   - energy 0.8 vs target 0.88 (+1.38)
   - danceability 0.9 vs target 0.85 (+0.95)

3. Rooftop Lights by Indigo Parade [indie pop / happy]
   Score: 3.29
   - mood match: happy (+1.00)
   - energy 0.76 vs target 0.88 (+1.32)
   - danceability 0.82 vs target 0.85 (+0.97)

4. Gym Hero by Max Pulse [pop / intense]
   Score: 2.40
   - energy 0.93 vs target 0.88 (+1.42)
   - danceability 0.88 vs target 0.85 (+0.97)

5. Fuego en la Calle by Rio Calma [latin / playful]
   Score: 2.38
   - energy 0.85 vs target 0.88 (+1.46)
   - danceability 0.92 vs target 0.85 (+0.93)

```

**Do the results feel right?** Sunrise City at #1 for the pop profile feels
right: it is pop, happy, and close in energy. Library Rain and Storm Runner
at #1 for lofi and rock feel right for the same reasons. A sad song at #1 for
"Sad But Hyper" feels only half right: it respects the mood but ignores the
high energy the listener asked for.

**What surprised me:** Gym Hero (pop, intense, energy 0.93) appeared in the top
5 for four of five profiles. In plain words: Gym Hero is loud and very
danceable, so for almost anyone who wants high-energy music it looks like a
decent match. It is #2 for the pop fan because it is pop (+2.0 points). For the
rock fan it matches on "intense" mood and energy. For the unknown-genre fan it
matches on energy and danceability alone. The catalog has too few songs for
anything else to beat it.

**Comparing pairs of profiles:**

| Pair | What changed and why it makes sense |
|---|---|
| Pop vs Lofi | No shared songs. Pop's top 5 are mostly energy 0.76-0.93 songs (one slow outlier, Soleil de Minuit at 0.45); lofi's are all 0.28-0.42. |
| Pop vs Rock | Both want high energy, but pop gets pop/happy songs and rock gets rock/intense ones. They share two songs: Gym Hero (pop genre for one, intense mood for the other) and Sunrise City (#1 for pop, only #5 for rock, on energy and danceability alone). |
| Pop vs Sad But Hyper | Both want pop. Soleil de Minuit jumps from #3 to #1 because the sad mood now matches. |
| Pop vs Unknown Genre | Both want happy, high energy. Without a genre match, the top 3 are simply the three happy songs. |
| Lofi vs Rock | Opposites, with no overlap. Lofi's top results have energy 0.35-0.42 and rock's have 0.88-0.91. |
| Lofi vs Sad But Hyper | No overlap, but Sad But Hyper's #4 and #5 (Blue Smoke Lullaby, Willow Creek Letters) are quiet songs a lofi fan might also like: the mood label beat the energy request. |
| Lofi vs Unknown Genre | No overlap. One wants quiet and studious, the other loud and happy. |
| Rock vs Sad But Hyper | Both have an energy target near 0.9, and both fall back on Gym Hero at #3. But rock's #1 is loud and Sad But Hyper's #1 is quiet, so only rock's energy and labels agree. |
| Rock vs Unknown Genre | Both want high energy. Rock gets rock/intense songs; the unknown-genre fan gets happy songs, with Gym Hero at #4 for energy alone. |
| Sad But Hyper vs Unknown Genre | Both ask for something the catalog cannot fully give. Sad But Hyper gets a genre-and-mood match with the wrong energy; Unknown Genre gets good energy and mood with no genre. |

**Experiment (weight shift):** see the README. Halving genre and doubling
energy improved the pop and "sad but hyper" results (fewer off-vibe songs
ranked high) and barely changed lofi and rock.

---

## 8. Future Work

- Give partial genre credit to related genres (for example, indie pop for a
  pop fan) so exact labels matter less.
- Use a steeper penalty for large energy gaps, so a 0.45 song cannot earn half
  credit against a 0.90 target.
- Score the other columns (acousticness, tempo, instrumentalness, mood tags)
  and avoid listing the same artist or genre repeatedly in the top results.

---

## 9. Personal Reflection

I learned that a recommender is a scoring rule plus a sort, and that the
weights are choices about what matters. What surprised me most was how
convincing a simple weighted score feels once each result comes with reasons.
I used an AI assistant to plan the features, generate the dataset and code,
and explain the math. I double-checked it by recomputing scores by hand, by
running the tests, and by catching places where its explanations were slightly
overstated. If I extended this, I would add related-genre credit and a steeper
energy penalty first.