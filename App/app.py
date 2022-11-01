import pandas as pd
import pickle
import requests
import streamlit as st


# fetch posters
def fetch_details(movie_id):
    api_key = "a94e70ee3d11b933929529d6b65278f3"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()

    poster_path = "https://image.tmdb.org/t/p/original/" + data["poster_path"]
    movie_overview = data["overview"]
    if data["homepage"] != "":
        movie_link = data["homepage"]
    else:
        movie_link = f"https://www.imdb.com/title/{data['imdb_id']}/"
    return poster_path, movie_overview, movie_link


# load pickle files
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))


# store the name of all movies in one place for select box
movies = pd.DataFrame(movies_dict)
movie_names = movies["title"]


# create a title for web app
st.title("Movie Recommendation System")


# create a select box for movie names
movie = st.selectbox(
    'Select a movie',
    movie_names)

st.write('You selected:', movie)


# create a function to recommend movies
def recommend(movie_name):
    movie_index = movies[movies["title"] == movie_name].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_overview = []
    recommended_movies_link = []

    for mov in movies_list:
        # find movie_id of movie
        movie_id = movies.iloc[mov[0]].id

        # add title of movie in recommended_movies list
        recommended_movies.append(movies.iloc[mov[0]].title)

        # fetch other details
        posters, overview, link = fetch_details(movie_id)
        recommended_movies_posters.append(posters)
        recommended_movies_overview.append(overview)
        recommended_movies_link.append(link)

    return recommended_movies, recommended_movies_posters, recommended_movies_overview, recommended_movies_link


if st.button("Recommend"):
    rec_movies, rec_mov_posters, rec_mov_overview, rec_mov_link = recommend(movie)

    for i in range(5):
        st.subheader(rec_movies[i])
        st.image((rec_mov_posters[i]), width=150)
        with st.expander("Overview"):
            st.write(rec_mov_overview[i])
            st.write("\n")
            st.write(f"URL: {rec_mov_link[i]}")
