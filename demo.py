import pandas as pd
import joblib

# Load the data using the old method
books = pd.read_pickle('books.pkl')
ratings = pd.read_pickle('ratings.pkl')
users = pd.read_pickle('users.pkl')
similarity_scores = pd.read_pickle('similarity_scores.pkl')
pt = pd.read_pickle('pt.pkl')
popbooks = pd.read_pickle('popbooks.pkl')

# Save the data using joblib
joblib.dump(books, 'books.pkl')
joblib.dump(ratings, 'ratings.pkl')
joblib.dump(users, 'users.pkl')
joblib.dump(similarity_scores, 'similarity_scores.pkl')
joblib.dump(pt, 'pt.pkl')
joblib.dump(popbooks, 'popbooks.pkl')