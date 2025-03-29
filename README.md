# Positive News App Documentation

## Project Overview

The Positive News App is a Streamlit-based web application that aggregates and displays positive news from various categories. The application fetches news from Google News RSS feeds, filters out negative content using sentiment analysis, and presents the news in a user-friendly interface.

## Features

- **Category-based News**: Browse news across multiple categories (Home, Technology, Entertainment, Business, Sports, Health, Politics, World)
- **Positive Content Filter**: Automatically filters out negative news using keyword detection and sentiment analysis
- **Search Functionality**: Search for specific topics while maintaining the positive content filter
- **Responsive UI**: Clean, modern interface inspired by Google News with category navigation
- **Pagination**: Navigate through multiple pages of news results
- **Source Recognition**: Visual differentiation of news sources with color-coded borders
- **Full Coverage Links**: Direct links to the original articles

## Technical Architecture

### Dependencies

The application relies on the following Python libraries:
- `streamlit`: For the web application framework
- `feedparser`: For parsing RSS feeds
- `vaderSentiment`: For sentiment analysis
- `PIL` (Pillow): For image processing
- `pandas`: For data handling (imported but not actively used)

### Core Components

#### 1. Data Sources
The application defines RSS feeds for various news categories using Google News RSS feeds for India:

```python
RSS_FEEDS = {
    "Home": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "Technology": "https://news.google.com/rss/search?q=technology+india&hl=en-IN&gl=IN&ceid=IN:en",
    # Additional categories...
}
```

#### 2. Content Filtering
Two levels of content filtering are implemented:

1. **Keyword-based filtering**: A predefined list of negative keywords is used to quickly filter out potentially negative news:
   ```python
   NEGATIVE_KEYWORDS = ["crime", "death", "accident", "murder", "violence", "suicide", 
                        # Additional keywords...
                       ]
   ```

2. **Sentiment Analysis**: Using VADER (Valence Aware Dictionary and sEntiment Reasoner) to perform sentiment analysis on news titles:
   ```python
   sentiment_score = analyzer.polarity_scores(title)['compound']
   # Allow only positive or neutral sentiment news (score >= 0.05)
   ```

#### 3. News Fetching
The application includes several functions for fetching news:
- `fetch_news()`: Gets news for a specific category with pagination
- `search_news()`: Fetches news matching a search query
- `fetch_news_by_subcategory()`: Gets news for specific subcategories (implemented but not actively used)

#### 4. UI Components
The UI is built with Streamlit and enhanced with custom CSS:
- Navigation bar with category buttons
- Search box
- News cards with source, title, publication time, and link
- Pagination controls

#### 5. Helper Functions
Several utility functions enhance the application:
- `extract_source()`: Identifies the news source
- `format_time()`: Converts timestamps to relative time (e.g., "2 hours ago")
- `get_base64_encoded_image()`: Handles icon encoding for the full coverage link

### Data Flow

1. User selects a category or enters a search term
2. Application fetches RSS feed from Google News
3. Content filtering removes negative news
4. Filtered articles are displayed with pagination
5. User can navigate through pages or change categories

## UI Design

The application features a clean, Google News-inspired interface with:
- A prominent search bar
- Category navigation at the top
- News cards with consistent styling
- Color-coded borders based on news source
- Pagination controls at the bottom

### Styling

The app uses custom CSS to create a consistent, professional appearance:
- Light theme with white background and dark text
- Card-based layout for news items
- Hover effects for interactive elements
- Responsive design for various screen sizes

## Implementation Details

### Session State Management
Streamlit's session state is used to maintain the application state:
```python
if "page" not in st.session_state:
    st.session_state.page = 0
    
if "active_category" not in st.session_state:
    st.session_state.active_category = "Home"
```

### Event Handling
Button clicks trigger state changes and page refreshes:
```python
if st.button("Tech", key="tech_btn", use_container_width=True):
    st.session_state.active_category = "Technology"
    st.session_state.page = 0
    st.session_state.reset_search = True
    st.rerun()
```

### Error Handling
The application includes error handling for RSS feed parsing and file operations:
```python
try:
    feed = feedparser.parse(url)
    # Process feed
except Exception as e:
    st.error(f"Error fetching {category} news: {str(e)}")
    return []
```

## Setup and Deployment

### Requirements
- Python 3.7 or higher
- Required libraries listed in requirements.txt:
  ```
  streamlit
  feedparser
  pillow
  vaderSentiment
  ```

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app.py
```

## Future Enhancements

Potential improvements for future versions:
1. User preferences for news categories and filters
2. Additional sentiment analysis refinement
3. Image previews for news articles
4. More subcategory options
5. User authentication for personalized experience

## Conclusion

The Positive News App successfully combines RSS feed aggregation, sentiment analysis, and a clean user interface to deliver a positive news browsing experience. By filtering out negative content, the application provides users with uplifting news across multiple categories while maintaining a professional, responsive interface.
