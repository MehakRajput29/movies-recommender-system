import os
import pickle
import pandas as pd
import requests
import streamlit as st
import gdown


st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

API_KEY = "4eb98061"

MOVIES_DICT_ID = "1vEBmhP_8AE7G6U-NkqKcqFKOVZbEH9K6"
SIMILARITY_ID = "1QQlFDYiM4Y9BprvIr2efvh2wrxc4tE-l"


# Automatic Cloud Data Loader
@st.cache_resource
def load_data():
    if not os.path.exists('movies_dict.pkl'):
        gdown.download(id=MOVIES_DICT_ID, output='movies_dict.pkl', quiet=False)

    if not os.path.exists('similarity.pkl'):
        gdown.download(id=SIMILARITY_ID, output='similarity.pkl', quiet=False)

    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()

# Custom CSS styling
st.markdown("""
    <style>
    /* Dark Slate Theme Background */
    .stApp {
        background-color: #12161f;
        color: #e2e8f0;
    }

    /* Header styling */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        text-align: center;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Style select box and button */
    div[data-baseweb="select"] {
        border-radius: 8px;
    }
    .stButton > button {
        width: 100%;
        background-color: #e11d48;
        color: white;
        border: none;
        padding: 0.55rem 1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #be123c;
        color: white;
        transform: translateY(-1px);
    }

    /* Recommendation Cards */
    .movie-card {
        text-align: center;
        background: #1e293b;
        padding: 10px;
        border-radius: 12px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        border: 1px solid #334155;
    }
    .movie-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
        border-color: #e11d48;
    }
    .movie-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 10px;
        color: #f8fafc;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def fetch_poster(movie_name):
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True" and data.get("Poster") != "N/A":
            return data.get("Poster")
    except Exception:
        pass
    return "https://via.placeholder.com/300x450/1e293b/ffffff?text=No+Poster"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_movies_posters.append(fetch_poster(movie_title))
    return recommended_movies, recommended_movies_posters


# Title Section
st.markdown('<p class="main-title">🎬 Movie Recommender System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Select a movie to get personalized recommendations</p>', unsafe_allow_html=True)

# Centered Control Section
left_spacer, center_col, right_spacer = st.columns([1, 2, 1])

with center_col:
    selected_movie_name = st.selectbox(
        'Select a movie:',
        movies['title'].values
    )
    btn_click = st.button('Get Recommendations')

st.markdown("<br>", unsafe_allow_html=True)

# Display Recommendations
if btn_click:
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(selected_movie_name)

        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{posters[idx]}" style="width: 100%; border-radius: 8px;" />
                        <div class="movie-title" title="{names[idx]}">{names[idx]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )