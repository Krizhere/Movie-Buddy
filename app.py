import os
import pickle

import gdown
import pandas as pd
import requests
import streamlit as st

MOVIE_FILE_ID = os.getenv("MOVIE_FILE_ID", "1IGwtMSKCGFsz60aUskDuX_EqORT_uOS9")
SIMILARITY_FILE_ID = os.getenv("SIMILARITY_FILE_ID", "1oX8Fq3iWzW0QD0fJ-7uX8rhlOHXSlcEA")


def ensure_drive_file(file_id, dest_path, label):
    if os.path.exists(dest_path):
        return
    if not file_id:
        st.error(f"Missing Google Drive file id for {label}. Set {label}_FILE_ID.")
        st.stop()
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, dest_path, quiet=False)

@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=No+Image"

        data = response.json()
        poster_path = data.get("poster_path")

        if not poster_path:
            return "https://via.placeholder.com/500x750?text=No+Image"

        return "https://image.tmdb.org/t/p/w500/" + poster_path

    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=No+Image"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

ensure_drive_file(MOVIE_FILE_ID, "movie.pkl", "MOVIE")
ensure_drive_file(SIMILARITY_FILE_ID, "similarity.pkl", "SIMILARITY")

movies_list = pickle.load(open("movie.pkl", "rb"))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open("similarity.pkl", "rb"))

st.title("Movie Recommender System")
selected_movie=st.selectbox("Select or Type Movie Name",movies['title'].values)

if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])
