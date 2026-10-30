# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
