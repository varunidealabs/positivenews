import streamlit as st
import feedparser
from datetime import datetime
import time
import re
from PIL import Image
import pandas as pd
import base64
import io
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Define RSS feed URLs
RSS_FEEDS = {
    "Home": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/search?q=technology+india&hl=en-IN&gl=IN&ceid=IN:en",
    "Entertainment": "https://news.google.com/rss/search?q=entertainment+india&hl=en-IN&gl=IN&ceid=IN:en",
    "Business": "https://news.google.com/rss/search?q=business+india&hl=en-IN&gl=IN&ceid=IN:en",
    "Sports": "https://news.google.com/rss/search?q=sports+india&hl=en-IN&gl=IN&ceid=IN:en",
    "Health": "https://news.google.com/rss/search?q=health+india&hl=en-IN&gl=IN&ceid=IN:en",
    "Politics": "https://news.google.com/rss/search?q=politics+india&hl=en-IN&gl=IN&ceid=IN:en",
    "World": "https://news.google.com/rss/search?q=world+news&hl=en-IN&gl=IN&ceid=IN:en"
}

# Define strong negative keyword list
NEGATIVE_KEYWORDS = ["crime", "death", "accident", "murder", "violence", "suicide", 
                     "attack", "tragedy", "disaster", "fraud", "scandal", "abuse", 
                     "corruption", "injury", "rape", "terrorism", "kidnapping", 
                     "war", "explosion", "massacre", "genocide"]

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to filter negative news with improved sentiment analysis
def filter_positive_news(articles):
    filtered_articles = []
    for article in articles:
        title = article.title
        summary = article.summary if hasattr(article, "summary") else ""
        
        # Step 1: Quick keyword check (Only on title for efficiency)
        if any(re.search(rf"\b{word}\b", title.lower()) for word in NEGATIVE_KEYWORDS):
            continue  # Skip if a negative keyword is found in the title
        
        # Step 2: Sentiment analysis using VADER
        sentiment_score = analyzer.polarity_scores(title)['compound']
        
        # Allow only positive or neutral sentiment news
        if sentiment_score >= 0.05:
            filtered_articles.append(article)
    
    return filtered_articles

# Function to fetch news
def fetch_news(category, page):
    url = RSS_FEEDS.get(category, RSS_FEEDS["Home"])
    try:
        feed = feedparser.parse(url)
        all_articles = filter_positive_news(feed.entries)
        return all_articles[page * 5:(page + 1) * 5] if len(all_articles) > page * 5 else all_articles
    except Exception as e:
        st.error(f"Error fetching {category} news: {str(e)}")
        return []

# Function to search news
def search_news(keyword):
    # Sanitize the search query by trimming whitespace and ensuring it's not empty
    keyword = keyword.strip()
    if not keyword:
        return []
        
    url = f"https://news.google.com/rss/search?q={keyword}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        feed = feedparser.parse(url)
        return filter_positive_news(feed.entries)
    except Exception as e:
        st.error(f"Error searching for '{keyword}': {str(e)}")
        return []

# Function to fetch news by subcategory
def fetch_news_by_subcategory(category, subcategory, page):
    if category == "Entertainment":
        if subcategory == "Latest":
            url = RSS_FEEDS["Entertainment"]
        else:
            # Search for subcategory within Entertainment
            url = f"https://news.google.com/rss/search?q=entertainment+india&hl=en-IN&gl=IN&ceid=IN:en"
    else:
        # Default to category feed
        url = RSS_FEEDS.get(category, RSS_FEEDS["Home"])
    
    try:
        feed = feedparser.parse(url)
        all_articles = filter_positive_news(feed.entries)
        return all_articles[page * 5:(page + 1) * 5] if len(all_articles) > page * 5 else all_articles
    except Exception as e:
        st.error(f"Error fetching {subcategory} news: {str(e)}")
        return []

# Function to extract source from article
def extract_source(article):
    if hasattr(article, "source"):
        return article.source.title
    else:
        # Try to extract source from title
        match = re.search(r'^(.*?) - ', article.title)
        if match:
            return match.group(1)
        return "News Source"

# Function to format time
def format_time(published_time):
    try:
        pub_time = datetime.strptime(published_time, "%a, %d %b %Y %H:%M:%S %Z")
        current_time = datetime.now()
        diff = current_time - pub_time
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds // 3600 > 0:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds // 60 > 0:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    except:
        return "Recently"

# Function to get base64 encoded image
def get_base64_encoded_image():
    try:
        with open("fullcoverage.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        # If error occurs, create and encode a blue icon
        # Create a small blue image
        img = Image.new('RGB', (20, 20), color=(66, 133, 244))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

# Streamlit UI
st.set_page_config(
    page_title="News App",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Get encoded image data
fullcoverage_img = get_base64_encoded_image()

# Initialize session states
if "page" not in st.session_state:
    st.session_state.page = 0
    
if "active_category" not in st.session_state:
    st.session_state.active_category = "Home"
    
if "reset_search" not in st.session_state:
    st.session_state.reset_search = False

# Initialize search value with empty string
search_value = ""
if not st.session_state.reset_search:
    # Only use previous search value if not resetting
    if "previous_search" in st.session_state:
        search_value = st.session_state.previous_search
else:
    # Reset flag after using it
    st.session_state.reset_search = False

# Custom CSS for styling the app - Light Theme version
st.markdown("""
<style>
    /* Light theme */
    .main {
        background-color: #ffffff;
        color: #202124;
    }
    .stApp {
        background-color: #ffffff;
    }
    
    /* App title styling */
    .app-title {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #202124;
    }
    
    /* Search box */
    .search-container {
        position: relative;
        margin-bottom: 20px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
    }
    
    [data-testid="stTextInput"] {
        max-width: 400px;
        margin: 0 auto;
    }
    
    input[type="text"] {
        width: 100%;
        padding: 10px 15px;
        border-radius: 20px !important;
        border: 1px solid #dadce0 !important;
        background-color: #f1f3f4 !important;
        color: #202124 !important;
        font-size: 16px !important;
    }
    
    input[type="text"]::placeholder {
        color: #5f6368 !important;
        opacity: 1 !important;
    }
    
    /* News card */
    .news-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 22px;
        margin-bottom: 22px;
        transition: transform 0.3s;
        border-left: 4px solid #4285f4;
        min-height: 160px;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
    }
    
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
    }
    
    .news-source {
        display: inline-block;
        font-size: 13px;
        font-weight: 600;
        color: #5f6368;
        margin-bottom: 10px;
    }
    
    .news-title {
        font-size: 18px;
        font-weight: 500;
        color: #202124;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    
    .news-time {
        font-size: 13px;
        color: #5f6368;
    }
    
    /* Category title */
    .category-title {
        font-size: 22px;
        font-weight: 500;
        margin-bottom: 15px;
        color: #202124;
        border-bottom: 2px solid #4285f4;
        padding-bottom: 5px;
        display: inline-block;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background-color: #dadce0;
        margin: 15px 0;
    }
    
    /* Full coverage link */
    .full-coverage {
        display: flex;
        align-items: center;
        color: #1a73e8;
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        margin-top: 10px;
    }
    
    .full-coverage img {
        width: 20px;
        height: 20px;
        margin-right: 5px;
    }
    
    /* Pagination */
    .pagination {
        display: flex;
        justify-content: space-between;
        margin-top: 30px;
        margin-bottom: 50px;
    }
    
    .pagination-btn {
        background-color: #f2f2f2;
        color: #1b1e1d;
        border: 1px solid #dadce0;
        padding: 8px 20px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.3s;
        display: flex;
        align-items: center;
    }
    
    .pagination-btn:hover {
        background-color: #e8f0fe;
    }
    
    .pagination-btn svg {
        width: 16px;
        height: 16px;
        margin-right: 5px;
    }
    
    .pagination-btn.next svg {
        margin-right: 0;
        margin-left: 5px;
    }
    
    /* Style for active button */
    .stButton button {
        background-color: #f2f2f2;
        color: #1b1e1d;
        border: none;
        border-radius: 0;
        padding: 10px 15px;
        font-size: 16px;
        transition: color 0.3s;
    }
    
    .stButton button:hover {
        color: #1a73e8;
        background-color: #e8f0fe;
    }
    
    /* Override Streamlit button styles */
    .stButton>button:focus:not(:active) {
        border-color: transparent;
        color: #1a73e8;
    }
    
    .stButton>button:active {
        background-color: #f8f9fa;
        color: #1a73e8;
    }
    
    /* Navbar container */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #f2f2f2;
        padding: 0;
        margin-bottom: 25px;
        border-radius: 5px;
        border-bottom: 1px solid #dadce0;
    }
    
    /* Column styling for navbar */
    .navbar [data-testid="column"] {
        padding: 0 !important;
    }
    
    /* Additional styling for subcategory buttons */
    .category-subcategory .stButton button {
        background-color: #f8f9fa;
        border-radius: 20px;
        margin-right: 8px;
        padding: 8px 15px;
        min-width: 0;
    }
    
    .category-subcategory .stButton button:hover,
    .category-subcategory .stButton button:active,
    .category-subcategory .stButton button:focus:not(:active) {
        background-color: #e8f0fe;
        color: #1a73e8;
    }
    
    /* Show subcategories button */
    .subcategory-button {
        text-align: center;
        margin-bottom: 15px;
    }
    
    .subcategory-button button {
        background-color: transparent !important;
        color: #1a73e8 !important;
        border: 1px solid #1a73e8 !important;
        border-radius: 20px !important;
        padding: 5px 15px !important;
        font-size: 12px !important;
    }
    
    .subcategory-button button:hover {
        background-color: rgba(26, 115, 232, 0.1) !important;
    }
    
    /* Pagination button alignment */
    .prev-button {
        text-align: left;
    }
    
    .next-button {
        text-align: right;
    }
    
    /* Remove Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Enforce full width */
    .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Search box - centered with reduced width
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_query = st.text_input("", placeholder="Search for topics like ai,cricket,...", key="search_box", value=search_value)
    
# Save current search for next render if not resetting
if not st.session_state.reset_search:
    st.session_state.previous_search = search_query

# Add a callback for category selection
def on_category_change():
    st.session_state.active_category = st.session_state.selected_category
    st.session_state.page = 0

# Main navigation with callbacks
st.markdown("<div class='navbar'>", unsafe_allow_html=True)
cols = st.columns(8)
with cols[0]:
    if st.button("Home", key="home_btn", use_container_width=True):
        st.session_state.active_category = "Home"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[1]:
    if st.button("Technology", key="tech_btn", use_container_width=True):
        st.session_state.active_category = "Technology"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[2]:
    if st.button("Entertainment", key="ent_btn", use_container_width=True):
        st.session_state.active_category = "Entertainment"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[3]:
    if st.button("Business", key="bus_btn", use_container_width=True):
        st.session_state.active_category = "Business"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[4]:
    if st.button("Sports", key="sports_btn", use_container_width=True):
        st.session_state.active_category = "Sports"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[5]:
    if st.button("Health", key="health_btn", use_container_width=True):
        st.session_state.active_category = "Health"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[6]:
    if st.button("Politics", key="politics_btn", use_container_width=True):
        st.session_state.active_category = "Politics"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
with cols[7]:
    if st.button("World", key="world_btn", use_container_width=True):
        st.session_state.active_category = "World"
        st.session_state.page = 0
        st.session_state.reset_search = True
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# Category tabs for subcategories - completely removed to show mixed entertainment news directly
# No subcategory options will be shown

# Get news based on search or category
if search_query:
    # Clean the search query for display
    clean_query = search_query.strip()
    if clean_query:
        st.markdown(f'<div class="category-title">Search Results for: {clean_query}</div>', unsafe_allow_html=True)
        articles = search_news(clean_query)
    else:
        st.markdown(f'<div class="category-title">Latest {st.session_state.active_category} News</div>', unsafe_allow_html=True)
        articles = fetch_news(st.session_state.active_category, st.session_state.page)
else:
    st.markdown(f'<div class="category-title">Latest {st.session_state.active_category} News</div>', unsafe_allow_html=True)
    articles = fetch_news(st.session_state.active_category, st.session_state.page)

# Display news articles
if not articles:
    st.markdown('<div class="news-card">No articles found. Try a different category or search query.</div>', unsafe_allow_html=True)
else:
    for article in articles:
        source = extract_source(article)
        published_time = article.published if hasattr(article, "published") else ""
        formatted_time = format_time(published_time)
        
        # Determine border color based on source
        border_color = "#4285f4"  # Default blue - Google's primary blue
        if "NDTV" in source:
            border_color = "#EA4335"  # Google's red
        elif "India Today" in source:
            border_color = "#FBBC05"  # Google's yellow
        elif "Economic Times" in source:
            border_color = "#34A853"  # Google's green
        
        st.markdown(f'''
        <div class="news-card" style="border-left: 4px solid {border_color}">
            <span class="news-source">{source}</span>
            <div class="news-title">{article.title}</div>
            <span class="news-time">{formatted_time}</span>
            <br>
            <a href="{article.link}" target="_blank" class="full-coverage">
                <img src="data:image/png;base64,{fullcoverage_img}" alt="full coverage icon" style="width:20px;height:20px;">
                Full coverage
            </a>
        </div>
        ''', unsafe_allow_html=True)

# Pagination with improved alignment
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("← Previous", key="prev", use_container_width=True) and st.session_state.page > 0:
        st.session_state.page -= 1
        st.rerun()
with col3:
    if st.button("Next →", key="next", use_container_width=True):
        st.session_state.page += 1
        st.rerun()

# Add debug info to the sidebar (hidden by default)
if st.sidebar.checkbox("Show Debug Info", value=False):
    st.sidebar.write("Active Category:", st.session_state.active_category)
    st.sidebar.write("Page:", st.session_state.page)
    st.sidebar.write("Search Query:", search_query)
    st.sidebar.write("Session State:", st.session_state)
