import os
import pickle
import gdown
import pandas as pd
import requests
import streamlit as st

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Movie Buddy",
    page_icon="🎬",
    layout="wide"
)

# ---------------- NETFLIX STYLE UI ---------------- #

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

h1 {
    text-align: center;
}

.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
}

.stImage img {
    border-radius: 12px;
    transition: transform .3s ease;
}

.stImage img:hover {
    transform: scale(1.08);
}

.movie-title {
    text-align: center;
    font-weight: bold;
    margin-top: 6px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- GOOGLE DRIVE FILE IDS ---------------- #

MOVIE_FILE_ID = os.getenv("MOVIE_FILE_ID", "1IGwtMSKCGFsz60aUskDuX_EqORT_uOS9")
SIMILARITY_FILE_ID = os.getenv("SIMILARITY_FILE_ID", "1oX8Fq3iWzW0QD0fJ-7uXSlcEA")

# ---------------- DOWNLOAD DATA ---------------- #

def ensure_drive_file(file_id, dest_path):
    if os.path.exists(dest_path):
        return

    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, dest_path, quiet=False)


# ---------------- FETCH POSTER ---------------- #

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

    except:
        return "https://via.placeholder.com/500x750?text=No+Image"


# ---------------- RECOMMENDATION FUNCTION ---------------- #

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


# ---------------- LOAD DATA ---------------- #

ensure_drive_file(MOVIE_FILE_ID, "movie.pkl")
ensure_drive_file(SIMILARITY_FILE_ID, "similarity.pkl")

movies_list = pickle.load(open("movie.pkl", "rb"))
movies = pd.DataFrame(movies_list)

similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- APP HEADER ---------------- #

st.title("🎬 Movie Buddy")
st.markdown("### Discover movies similar to your favorites")

st.markdown("---")

# ---------------- MOVIE SELECT ---------------- #

selected_movie = st.selectbox(
    "Select or type a movie",
    movies['title'].values
)

# ---------------- BUTTON ---------------- #

if st.button("🍿 Recommend Movies"):

    with st.spinner("Finding similar movies..."):

        names, posters = recommend(selected_movie)

    st.markdown("## Recommended Movies")

    cols = st.columns(5)

    for i in range(5):

        with cols[i]:

            st.image(posters[i])

            st.markdown(
                f"<div class='movie-title'>{names[i]}</div>",
                unsafe_allow_html=True
            )

# ---------------- FOOTER ---------------- #

st.markdown("---")
st.caption("Built with ❤️ using Python, Streamlit & Machine Learning")
