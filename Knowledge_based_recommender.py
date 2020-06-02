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

# creating new features exploding genres
g = know_data.apply(lambda x: pd.Series(x['genres']), axis = 1).stack().reset_index(level = 1, drop = True)

g.name = 'genres'

gen_data = know_data.drop('genres', axis = 1).join(g)
#gen_data.head()

def build_chart(gen_df, percentile = 0.8):
    print("Input preferred genre")
    genre = input().lower() #user interested input
    
    #Ask for minimum duration
    print("Input shortest duration")
    min_time = int(input())
    
    #Ask for maximum duration
    print("Input longest duration")
    max_time = int(input())
    
    #Ask for lower limit of timeline
    print("Input earliest year")
    start_year = int(input())
    
    #Ask for upper limit of timeline
    print("Input latest year")
    lat_year = int(input())
    
    movies = gen_df.copy()
    
    #Filter based on the condition
    movies = movies[(movies['genres'] == genre) & 
                    (movies['runtime'] >= min_time) & 
                    (movies['runtime'] <= max_time) & 
                    (movies['year'] >= start_year) & 
                    (movies['year'] <= lat_year)]
    
    #Compute the values of C and m for the filtered movies
    C = movies['vote_average'].mean()
    m = movies['vote_count'].quantile(percentile)
    q_movies = movies.copy().loc[movies['vote_count'] >= m]
    #Calculate score using the IMDB formula
    q_movies['score'] = q_movies.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C),axis=1)
    
    #Sort movies in descending order of their scores
    q_movies = q_movies.sort_values('score', ascending=False)
    
    return q_movies
	
show = build_chart(gen_data)
print(show.head(10))