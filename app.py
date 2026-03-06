import os
import pickle
import gdown
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Movie Buddy", page_icon="🎬", layout="wide")

MOVIE_FILE_ID = os.getenv("MOVIE_FILE_ID", "1IGwtMSKCGFsz60aUskDuX_EqORT_uOS9")
SIMILARITY_FILE_ID = os.getenv("SIMILARITY_FILE_ID", "1oX8Fq3iWzW0QD0fJ-7uXSlcEA")


def ensure_drive_file(file_id, dest_path, label):
    if os.path.exists(dest_path):
        return
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, dest_path, quiet=False)


@st.cache_data
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url)

        if response.status_code != 200:
            return "https://via.placeholder.com/500x750?text=No+Image"

        data = response.json()
        poster_path = data.get("poster_path")

        if not poster_path:
            return "https://via.placeholder.com/500x750?text=No+Image"

        return "https://image.tmdb.org/t/p/w500/" + poster_path

    except:
        return "https://via.placeholder.com/500x750?text=No+Image"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


ensure_drive_file(MOVIE_FILE_ID, "movie.pkl", "MOVIE")
ensure_drive_file(SIMILARITY_FILE_ID, "similarity.pkl", "SIMILARITY")

movies_list = pickle.load(open("movie.pkl", "rb"))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- UI ---------------- #

st.title("🎬 Movie Buddy")
st.markdown("### Discover movies similar to your favorites")

selected_movie = st.selectbox(
    "Select a Movie",
    movies['title'].values
)

if st.button("Recommend Movies 🍿"):

    with st.spinner("Finding similar movies..."):
        names, posters = recommend(selected_movie)

    st.markdown("---")
    st.subheader("Recommended Movies")

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.image(posters[i])
            st.markdown(
                f"<p style='text-align:center;font-weight:bold'>{names[i]}</p>",
                unsafe_allow_html=True
            )
