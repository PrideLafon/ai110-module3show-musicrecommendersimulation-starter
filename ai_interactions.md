# AI Interactions Log

## Agentic Workflow (SF8)

**What task did you give the agent?**

I asked Claude (in a chat window) to work through the whole Music
Recommender project with me, including every optional stretch feature. For
this stretch feature the task was: add more song attributes to the dataset
and update the scoring so the new attributes affect the recommendations.
Claude wrote the code and also ran it in its own sandbox before giving it to
me. I ran everything again on my machine (Windows, VS Code, Python 3.14,
a venv) and pasted back errors and outputs.

**Prompts used:**

- "I want us to work meticulously on this project" (with the full assignment
  and rubric pasted in)
- "we do everything even the optional"
- "I mean you should be providing the solutions"
- "Continue" / "go" (to move on to each next stretch feature)

**What did the agent generate or change?**

- `data/songs.csv`: expanded from 10 to 24 songs and added five new columns:
  `popularity`, `release_decade`, `mood_tags`, `language`, `instrumentalness`.
- `src/recommender.py`: scoring now also uses `acousticness`,
  `instrumentalness`, `popularity`, `release_decade`, `mood_tags` and
  `language`. These are optional: a feature is scored only when the listener
  profile gives a preference for it, so older profiles score exactly as before.
- `src/main.py`: a new "Rainy Study Session" profile that uses the extras.
- `tests/test_recommender.py`: three new tests (instrumental preference,
  language match, mood-tag overlap).
- `README.md` and `model_card.md`: