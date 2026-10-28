import streamlit as st
import pandas as pd
import random

st.set_page_config(
    page_title="SoundMetrics | Discover Music",
    page_icon="🎧",
    layout="wide"
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #10101c, #17152b, #101820);
    color: #ffffff;
}
h1, h2, h3 { color: #ffffff; }
div[data-testid="stMetric"] {
    background: #22223a;
    padding: 16px;
    border-radius: 14px;
}
.song-card {
    background: #22223a;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #454568;
}
div.stButton > button {
    background: #b9ff66;
    color: #111111;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------- Load dataset ----------
@st.cache_data
def load_data():
    data = pd.read_csv("soundmetrics_songs.csv")
    data["duration_minutes"] = pd.to_numeric(
        data["duration_minutes"], errors="coerce"
    )
    data["release_year"] = pd.to_numeric(
        data["release_year"], errors="coerce"
    )
    return data

df = load_data()

# ---------- Header ----------
st.title("🎧 SoundMetrics")
st.markdown("### The Data Behind the Beat")
st.write("Discover music through artist-based recommendations and data insights.")

st.divider()

# ---------- Sidebar ----------
st.sidebar.title("🎵 Your Music")
artists = sorted(df["selected_artist"].dropna().unique())

selected_artist = st.sidebar.selectbox(
    "Choose your artist",
    artists
)

st.sidebar.caption(
    "SoundMetrics uses a transparent, rule-based recommendation prototype."
)

# ---------- Recommendation ----------
artist_songs = df[
    df["selected_artist"] == selected_artist
].copy()

artist_songs = artist_songs.dropna(subset=["track_name"])

if st.button("✨ Discover My Song"):
    if not artist_songs.empty:
        artist_songs["duration_score"] = (
            1 - (artist_songs["duration_minutes"] - 3.5).abs() / 3.5
        ).clip(0, 1)

        artist_songs["score"] = (
            artist_songs["duration_score"].fillna(0) * 0.7
            + artist_songs["preview_url"].notna().astype(int) * 0.3
        )

        top_songs = artist_songs.sort_values(
            "score", ascending=False
        ).head(min(5, len(artist_songs)))

        song = top_songs.sample(1).iloc[0]

        st.session_state["recommended_song"] = song.to_dict()
        st.session_state["recommended_artist"] = selected_artist

if "recommended_song" in st.session_state:
    song = st.session_state["recommended_song"]

    st.markdown("## 💚 Your SoundMetrics Pick")

    left, right = st.columns([1, 2])

    with left:
        artwork = song.get("artwork_url")
        if pd.notna(artwork) and str(artwork).startswith("http"):
            st.image(artwork, use_container_width=True)
        else:
            st.markdown("🎵")

    with right:
        st.markdown(f"### {song['track_name']}")
        st.write(f"**Artist:** {song['artist_name']}")
        st.write(f"**Album:** {song.get('album', 'Not available')}")

        duration = song.get("duration_minutes")
        if pd.notna(duration):
            st.write(f"**Duration:** {duration:.2f} minutes")

        preview = song.get("preview_url")
        if pd.notna(preview) and str(preview).startswith("http"):
            st.write("**Listen to the preview:**")
            st.audio(preview)
        else:
            st.info("Preview unavailable for this song.")

        full_link = song.get("song_url")
        if pd.notna(full_link) and str(full_link).startswith("http"):
            st.link_button("🎧 Open Full Song on Apple Music", full_link)

        st.caption(
            "Recommendation logic: songs are ranked using duration "
            "similarity to 3.5 minutes and preview availability. "
            "This is a prototype score, not a measured popularity ranking."
        )

st.divider()

# ---------- Data Science Insights ----------
st.header("📊 Behind the Music")
st.write("Explore the dataset used by the SoundMetrics recommendation prototype.")

m1, m2, m3 = st.columns(3)

m1.metric("Songs in Dataset", f"{len(df):,}")
m2.metric("Artists", f"{df['selected_artist'].nunique()}")
m3.metric(
    "Songs with Previews",
    f"{df['preview_url'].notna().sum():,}"
)

tab1, tab2, tab3 = st.tabs([
    "🎤 Artist Overview",
    "⏱️ Song Duration",
    "📅 Release Trends"
])

with tab1:
    artist_counts = (
        df.groupby("selected_artist")["track_name"]
        .count()
        .sort_values(ascending=False)
    )
    st.bar_chart(artist_counts)
    st.caption("Number of collected tracks per selected artist.")

with tab2:
    duration_data = df.dropna(subset=["duration_minutes"])
    st.bar_chart(
        duration_data.groupby("selected_artist")["duration_minutes"].mean()
    )
    st.caption("Average track duration by selected artist, in minutes.")

with tab3:
    year_data = df.dropna(subset=["release_year"]).copy()
    year_counts = year_data.groupby("release_year")["track_name"].count()
    st.line_chart(year_counts)
    st.caption("Collected track counts by release year.")

with st.expander("🔎 Explore song records"):
    st.dataframe(
        df[[
            "track_name", "artist_name", "selected_artist",
            "album", "release_year", "duration_minutes"
        ]],
        use_container_width=True
    )

st.divider()
st.caption(
    "SoundMetrics | Fundamentals of Data Science and Analytics | "
    "Data sourced from the Apple iTunes Search API."
)
