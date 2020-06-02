import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from ast import literal_eval

import os
os.chdir('C:\\Users\\deeks\\Downloads\\ipnynb_files\\data\\recommender')

meta_data = pd.read_csv('movies_metadata.csv')

know_data = meta_data[['title', 'release_date', 'vote_average', 'vote_count', 'runtime', 'genres']]

#Convert release_date into pandas datetime format
know_data['release_date'] = pd.to_datetime(know_data['release_date'], errors='coerce')

#Extract year from the datetime
know_data['year'] = know_data['release_date'].apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

def convert_int(x):
    try:
        return int(x)
    except:
        return 0
		
#Apply convert_int to the year feature
know_data['year'] = know_data['year'].apply(convert_int)

#Drop the release_date column
know_data = know_data.drop('release_date', axis=1)

know_data['genres'] = know_data['genres'].fillna('[]')

know_data['genres'] = know_data['genres'].apply(literal_eval)

know_data['genres'] = know_data['genres'].apply(lambda x: [i['name'].lower() for i in x] if isinstance(x, list) else [])


#Add the useful features into the cleaned dataframe
know_data['overview'], know_data['id'] = meta_data['overview'], meta_data['id']


from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(stop_words = 'english')

know_data['overview'] = know_data['overview'].fillna('')

tfidf_matrix = tfidf.fit_transform(know_data['overview'])

from sklearn.metrics.pairwise import linear_kernel
cosine_sim = linear_kernel(tfidf_matrix,tfidf_matrix)

#Construct a reverse mapping of indices and movie titles, and drop duplicat 
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

# Function that takes in movie title as input and gives recommendations 
def content_recommender(title, cosine_sim=cosine_sim, df=df, indices=indices):
    # Obtain the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    # And convert it into a list of tuples as described above
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the cosine similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies. Ignore the first movie.
    sim_scores = sim_scores[1:11]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return df['title'].iloc[movie_indices]
	
inp_movie = input('Type movie name to find similar ones').lower()

print(content_recommender(inp_movie))