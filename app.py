import streamlit as st
import pickle
import numpy as np
import pandas as pd

# ------------------------- Page Configuration -------------------------
st.set_page_config(page_title="Book Recommender System", layout="wide")

# ------------------------- Custom CSS Styling -------------------------
page_bg_img = '''
<style>
.stApp {
    background: linear-gradient(to right, rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
                url("https://images.unsplash.com/photo-1507842217343-583bb7270b66");
    background-size: cover;
    background-attachment: fixed;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3, h4, h5, h6, .stMarkdown, .stTextInput > label,
.stSelectbox > label, .stButton > button, .stCaption, .stAlert {
    color: white !important;
}
.stButton > button {
    background-color: #5e5e5e;
    border: 1px solid #ddd;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    transition: 0.3s ease;
}
.stButton > button:hover {
    background-color: #888;
}
img {
    border-radius: 10px;
    transition: transform 0.3s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6);
}
img:hover {
    transform: scale(1.03);
}
.book-card {
    background: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 15px;
}
.book-title {
    font-weight: bold;
    font-size: 16px;
    margin-top: 10px;
}
.book-author {
    font-size: 14px;
    color: #ccc;
    margin-bottom: 8px;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# ------------------------- Sidebar Navigation -------------------------
page = st.sidebar.radio("Navigate", ["Home", "Top 50 Popular Books", "Book Recommendation"])

# ------------------------- Load Data -------------------------
try:
    popular_df = pickle.load(open('df.pkl', 'rb'))
    pt = pickle.load(open('pivot.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_score.pkl', 'rb'))
except FileNotFoundError:
    st.error("One or more .pkl files are missing. Please ensure all files are present.")
    st.stop()

# ------------------------- Recommend Function -------------------------
def recommend(book_name):
    try:
        index = np.where(pt.index == book_name)[0][0]
    except IndexError:
        return pd.DataFrame(), "Book not found in our database."
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]
    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        book_info = temp_df.drop_duplicates('Book-Title')[['Book-Title', 'Book-Author', 'Image-URL-M']].values[0]
        data.append(book_info)
    return pd.DataFrame(data, columns=['Book-Title', 'Book-Author', 'Image-URL-M']), None

# ------------------------- Page: Home -------------------------
if page == "Home":
    st.markdown("<h1 style='text-align: center; margin-top: 3rem; font-size: 42px;'>Book Recommender System</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; max-width: 800px; margin: auto; font-size: 18px; padding-top: 10px; line-height: 1.8;'>
        This application helps you explore the world of books by offering personalized recommendations and titles.<br><br>
        Whether you're a casual reader or a dedicated bibliophile, you’ll discover books you'll love.
        <br><br>
        <b>Features:</b><br>
        • View the Top 50 Popular Books<br>
        • Get Recommendations Based on Your Favorite Book<br>
        • Clean and elegant interface<br><br>
        Use the sidebar to get started.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    # st.image("https://images.unsplash.com/photo-1606112219348-204d7d8b94ee", use_container_width=True)

# ------------------------- Page: Top 50 Popular Books -------------------------
elif page == "Top 50 Popular Books":
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Top 50 Popular Books</h1>", unsafe_allow_html=True)

    search_query = st.text_input("Search by title or author (optional):")
    top_books = popular_df.head(50)

    if search_query:
        top_books = top_books[top_books['Book-Title'].str.contains(search_query, case=False, na=False) |
                              top_books['Book-Author'].str.contains(search_query, case=False, na=False)]

    num_cols = 5
    for i in range(0, len(top_books), num_cols):
        row_books = top_books.iloc[i:i+num_cols]
        cols = st.columns(num_cols)
        for col, (_, row) in zip(cols, row_books.iterrows()):
            with col:
                st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                st.image(row['Image-URL-M'], use_container_width=True)
                st.markdown(f"<div class='book-title'>{row['Book-Title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='book-author'>by {row['Book-Author']}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# ------------------------- Page: Book Recommendation -------------------------
elif page == "Book Recommendation":
    st.markdown("<h1 style='text-align: center;'>Book Recommender System</h1>", unsafe_allow_html=True)
    st.header("Book Recommendation")

    selected_book_name = st.selectbox(
        'Type or select a book from the dropdown:',
        pt.index.values,
        help="Start typing a title to quickly find a match."
    )

    if st.button('Show Recommendation'):
        with st.spinner('Finding your next great read...'):
            recommended_books_df, error_message = recommend(selected_book_name)
            if error_message:
                st.warning(error_message)
            elif not recommended_books_df.empty:
                st.markdown("<h3>Recommended Books:</h3>", unsafe_allow_html=True)
                num_cols = 5
                cols = st.columns(num_cols)
                for i, row in recommended_books_df.iterrows():
                    with cols[i % num_cols]:
                        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
                        st.image(row['Image-URL-M'], use_container_width=True)
                        st.markdown(f"<div class='book-title'>{row['Book-Title']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='book-author'>by {row['Book-Author']}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No recommendations found for this book.")
