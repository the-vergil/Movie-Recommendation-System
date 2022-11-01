# -*- coding: utf-8 -*-
"""Movie-Recommendation-System.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17c0KvggOJZ0LRYAIHQCxRswmz1pB5Ii8

# Step 1: Import dependencies
"""

import numpy as np
import pandas as pd
import ast
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")

"""# Step 2: Load data

"""

!pip install -U -q PyDrive

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
 
 
# Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

link1 = "https://drive.google.com/file/d/1MOYgqBQZ_dnmydOA9bQF65X4h64k4Mhi/view?usp=share_link"
link2 = "https://drive.google.com/file/d/1HWi2agYVFsjrUITMzPTYWDMo66Llte5F/view?usp=share_link"

id1 = link1.split("/")[-2]
id2 = link2.split("/")[-2]

downloaded1 = drive.CreateFile({'id':id1})
downloaded1.GetContentFile('tmdb_5000_credits.csv') 

downloaded2 = drive.CreateFile({'id':id2})
downloaded2.GetContentFile('tmdb_5000_movies.csv')

credits_data = pd.read_csv("tmdb_5000_credits.csv")
movies_data = pd.read_csv("tmdb_5000_movies.csv")

"""# Step 3: Merging data"""

print(f"Shape: {credits_data.shape}\n***********************")
credits_data.head(2)

print(f"Shape: {movies_data.shape}\n***********************")
movies_data.head(2)

movies = movies_data.merge(credits_data, on="title")

movies.head(1)

movies.shape

"""# Step 4: Feature selection

Since this recommendation system is a content-based-recommendation-system hence important tags are required on the basis of which movies will be matched
- Features required
  - genres
  - id
  - keywords
  - overview
  - title
  - cast
  - crew
"""

movies = movies[["title", "id", "genres", "keywords", "cast", "crew", "overview"]]
movies.head(3)

"""# Step 5: Data cleaning and preprocessing

## Data cleaning
"""

# checking number of duplicated rows
movies.duplicated().sum()

# checking null values
movies.isnull().sum()

# dropping rows containing null values
movies = movies.dropna()
# resetting the index
movies = movies.reset_index(drop=True)

"""## Data preprocessing"""

movies.head(1)

"""### Extracting genres"""

movies.iloc[0]["genres"]

# converting a string representation of list into list
ast.literal_eval(movies.iloc[0]["genres"])

# creating a function to extract genres
def get_genres(genres):
  genres = ast.literal_eval(genres)
  genre_list = []
  for dictionary in genres:
    genre_list.append(dictionary["name"])
  return genre_list

get_genres(movies.iloc[0]["genres"])

## apply the get_genres function on the whole column
movies["genres"] = movies["genres"].apply(lambda x: get_genres(x))

"""### Extracting keywords"""

movies.iloc[0]["keywords"]

# converting a string representation of list into list
ast.literal_eval(movies.iloc[0]["keywords"])

# creating a function to extract keywords
def get_keywords(keywords):
  keywords = ast.literal_eval(keywords)
  keywords_list = []
  for dictionary in keywords:
    keywords_list.append(dictionary["name"])
  return keywords_list

get_keywords(movies.iloc[0]["keywords"])

## apply the get_keywords function on the whole column
movies["keywords"] = movies["keywords"].apply(lambda x: get_keywords(x))

"""### Extracting cast"""

movies.head(1)

movies.iloc[0]["cast"]

# creating a function to extract top 5 cast cast members
def get_cast(cast):
  cast = ast.literal_eval(cast)
  cast_list = []
  counter = 0
  for dictionary in cast:
    if counter<5:
      cast_list.append(dictionary["name"])
      counter += 1
    else:
      break
  return cast_list

get_cast(movies.iloc[0]["cast"])

## apply the get_cast function on the whole column
movies["cast"] = movies["cast"].apply(lambda x: get_cast(x))

"""### Extracting crew (only director name)"""

movies.head(1)

movies.iloc[0]["crew"]

# creating a function to extract the name of director
def get_crew(crew):
  crew = ast.literal_eval(crew)
  crew_list = []
  for dictionary in crew:
    if dictionary["job"] == "Director":
      crew_list.append(dictionary["name"])
      break
  return crew_list

get_crew(movies.iloc[0]["crew"])

## apply the get_crew function on the whole column
movies["crew"] = movies["crew"].apply(lambda x: get_crew(x))

"""### Remove spaces from tags(genres, keywords, cast, crew) to uniquely identify tags"""

movies.head(1)

movies["genres"] = movies["genres"].apply(lambda x: [tag.replace(" ", "") for tag in x])
movies["keywords"] = movies["keywords"].apply(lambda x: [tag.replace(" ", "") for tag in x])
movies["cast"] = movies["cast"].apply(lambda x: [tag.replace(" ", "") for tag in x])
movies["crew"] = movies["crew"].apply(lambda x: [tag.replace(" ", "") for tag in x])

movies.head(1)

"""### Combining multiple columns to form a single column"""

movies["overview"] = movies["overview"].apply(lambda x: x.split(" "))

movies["tags"] = movies["genres"] + movies["keywords"] + movies["cast"] + movies["cast"] + movies["crew"] + movies["overview"]
movies.head(1)

movies = movies[["title", "id", "tags"]]
movies.head(1)

movies["tags"] = movies["tags"].apply(lambda x: " ".join(x))

movies.iloc[0]["tags"]

"""# Step 6: Count Vectorization"""

movies.head(1)

# lowercase all the text in tags
movies["tags"] = movies["tags"].apply(lambda x: x.lower())

def preprocess_tags(text):
  ps = PorterStemmer()

  # removing punctuation
  text = re.sub(r'[^\w\s]', '', text)

  # converting words in a list
  text = word_tokenize(text)

  # removing stopwords and stemming each word
  text = [ps.stem(word) for word in text if word not in stopwords.words("english")]

  # combing all words to form a string
  text = " ".join(text)
  
  return text

movies["preprocessed_tags"] = movies["tags"].apply(lambda x: preprocess_tags(x))

movies.iloc[0]["preprocessed_tags"]

cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(movies["preprocessed_tags"]).toarray()

vectors[0]

"""# Step 7: Cosine similarity"""

cos_sim = cosine_similarity(vectors)

cos_sim.shape

cos_sim[0]

"""# Step 8: Recommendation System"""

def recommend(movie):
  movie_index = movies[movies["title"]==movie].index[0]
  distances = cos_sim[movie_index]
  movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

  for movie in movies_list:
    print(movies.iloc[movie[0]].title)

recommend("The Wolverine")

"""# Step 9: Pickling"""

import pickle

pickle.dump(cos_sim, open("similarity.pkl", "wb"))

pickle.dump(movies.to_dict(), open("movies_dict.pkl", "wb"))