"""
Streamlit app for collecting human feedback on Drake lyrics sentiment analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import json
import sqlite3
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Drake Lyrics Sentiment Feedback",
    page_icon="🎵",
    layout="wide"
)

# Utility functions for database operations
@st.cache_resource
def get_connection(db_path):
    """Create a cached database connection"""
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    # Connect with extended timeout and disable same thread check for Streamlit
    return sqlite3.connect(db_path, timeout=30, check_same_thread=False)

class SentimentDatabase:
    def __init__(self, db_path="./.streamlit/drake_sentiment.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self._initialize_db()
    
    def _get_connection(self):
        """Get a database connection"""
        try:
            # Use cached connection
            return get_connection(self.db_path)
        except Exception as e:
            st.error(f"Database connection error: {e}")
            # Fallback to in-memory if there's an error
            return sqlite3.connect(":memory:")
    
    def _initialize_db(self):
        """Initialize database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create songs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            album TEXT,
            release_date TEXT,
            lyrics TEXT NOT NULL,
            lyrics_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create sentiment_analysis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            sentiment_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
        ''')
        
        # Create sentiment_qa table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_qa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            sentiment_analysis_id INTEGER NOT NULL,
            explanation TEXT,
            feedback TEXT,
            is_accurate BOOLEAN,
            reviewer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (song_id) REFERENCES songs (id),
            FOREIGN KEY (sentiment_analysis_id) REFERENCES sentiment_analysis (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_sentiment_analyses(self, model_name=None):
        """Get sentiment analyses from the database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if model_name:
                cursor.execute('''
                SELECT sa.id, sa.song_id, s.title, sa.model_name, sa.sentiment_score, sa.sentiment_category
                FROM sentiment_analysis sa
                JOIN songs s ON sa.song_id = s.id
                WHERE sa.model_name = ?
                ''', (model_name,))
            else:
                cursor.execute('''
                SELECT sa.id, sa.song_id, s.title, sa.model_name, sa.sentiment_score, sa.sentiment_category
                FROM sentiment_analysis sa
                JOIN songs s ON sa.song_id = s.id
                ''')
            
            results = cursor.fetchall()
            
            analyses = []
            for row in results:
                analyses.append({
                    'id': row[0],
                    'song_id': row[1],
                    'title': row[2],
                    'model_name': row[3],
                    'sentiment_score': row[4],
                    'sentiment_category': row[5]
                })
            
            return analyses
        except Exception as e:
            st.error(f"Error retrieving sentiment analyses: {str(e)}")
            return []
    
    def save_sentiment_analysis(self, song_id, model_name, sentiment_score, sentiment_category=None):
        """Save a sentiment analysis to the database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO sentiment_analysis (song_id, model_name, sentiment_score, sentiment_category)
            VALUES (?, ?, ?, ?)
            ''', (song_id, model_name, sentiment_score, sentiment_category))
            
            sa_id = cursor.lastrowid
            
            conn.commit()
            
            return sa_id
        except Exception as e:
            st.error(f"Error saving sentiment analysis: {str(e)}")
            return None

# Initialize sample data
def initialize_sample_data(db):
    """Initialize sample data if database is empty"""
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        
        # Check if we have any songs
        cursor.execute("SELECT COUNT(*) FROM songs")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Load sample data from data directory
            try:
                # Add sample songs
                sample_songs = [
                    ("Hotline Bling", "Views", "2016-04-29", 
                     "You used to call me on my cell phone\nLate night when you need my love\nCall me on my cell phone\nLate night when you need my love\nI know when that hotline bling\nThat can only mean one thing\nI know when that hotline bling\nThat can only mean one thing", 
                     "https://genius.com/Drake-hotline-bling-lyrics"),
                    ("God's Plan", "Scorpion", "2018-06-29", 
                     "Yeah, they wishin' and wishin' and wishin' and wishin'\nThey wishin' on me, yeah\nI been movin' calm, don't start no trouble with me\nTryna keep it peaceful is a struggle for me\nDon't pull up at 6 AM to cuddle with me\nYou know how I like it when you lovin' on me\nI don't wanna die for them",
                     "https://genius.com/Drake-gods-plan-lyrics"),
                ]
                
                # Insert each sample song into the database
                for song in sample_songs:
                    cursor.execute('''
                    INSERT INTO songs (title, album, release_date, lyrics, lyrics_url)
                    VALUES (?, ?, ?, ?, ?)
                    ''', song)
                    
                    song_id = cursor.lastrowid
                    
                    # Add sample sentiment analysis
                    db.save_sentiment_analysis(song_id, "VADER", 0.5, "Neutral")
                    db.save_sentiment_analysis(song_id, "TextBlob", 0.3, "Slightly Positive")
                
                conn.commit()
                
            except Exception as e:
                st.error(f"Error adding sample data: {str(e)}")
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")


# Main application
def main():
    st.title("Drake Lyrics Sentiment Analysis Feedback")
    
    # Initialize database
    db = SentimentDatabase()
    initialize_sample_data(db)
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["Home", "Provide Feedback", "View Analytics"])
    
    if page == "Home":
        st.header("Welcome to Drake Lyrics Sentiment Analysis Feedback")
        st.write("""
        This application allows you to review sentiment analysis performed on Drake's lyrics and provide feedback on the accuracy of the analysis.
        
        **How it works:**
        1. We analyze Drake's lyrics using various sentiment analysis models
        2. You review the analysis and provide feedback
        3. Your feedback helps improve sentiment analysis for music lyrics
        
        Use the sidebar to navigate through the application.
        """)
        
        # Display a sample of analyses
        st.subheader("Recent Sentiment Analyses")
        analyses = db.get_sentiment_analyses()
        if analyses:
            df = pd.DataFrame(analyses)
            st.dataframe(df)
        else:
            st.info("No sentiment analyses available yet.")
    
    elif page == "Provide Feedback":
        st.header("Provide Feedback on Sentiment Analysis")
        
        # Get available analyses
        analyses = db.get_sentiment_analyses()
        if not analyses:
            st.warning("No sentiment analyses available for feedback.")
            return
        
        # Select a song to review
        song_options = [(a['id'], f"{a['title']} ({a['model_name']})") for a in analyses]
        selected = st.selectbox("Select a song analysis to review:", 
                               options=range(len(song_options)),
                               format_func=lambda x: song_options[x][1])
        
        selected_analysis = analyses[selected]
        
        st.write(f"**Song:** {selected_analysis['title']}")
        st.write(f"**Model:** {selected_analysis['model_name']}")
        st.write(f"**Sentiment Score:** {selected_analysis['sentiment_score']}")
        st.write(f"**Sentiment Category:** {selected_analysis['sentiment_category'] or 'Not categorized'}")
        
        # Feedback form
        with st.form("feedback_form"):
            is_accurate = st.radio("Is this sentiment analysis accurate?", ["Yes", "No", "Partially"])
            explanation = st.text_area("Why do you think this?", height=100)
            reviewer = st.text_input("Your name (optional)")
            feedback = st.text_area("Additional feedback", height=150)
            
            submit = st.form_submit_button("Submit Feedback")
            
            if submit:
                if explanation:
                    try:
                        # Convert radio selection to boolean for database
                        is_accurate_bool = None
                        if is_accurate == "Yes":
                            is_accurate_bool = True
                        elif is_accurate == "No":
                            is_accurate_bool = False
                        
                        # Save to database
                        conn = db._get_connection()
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                        INSERT INTO sentiment_qa 
                        (song_id, sentiment_analysis_id, explanation, feedback, is_accurate, reviewer)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            selected_analysis['song_id'],
                            selected_analysis['id'],
                            explanation,
                            feedback,
                            is_accurate_bool,
                            reviewer
                        ))
                        
                        conn.commit()
                        
                        st.success("Thank you for your feedback!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saving feedback: {str(e)}")
                else:
                    st.error("Please provide an explanation for your feedback.")
    
    elif page == "View Analytics":
        st.header("Sentiment Analysis Analytics")
        
        # Display a basic chart
        st.subheader("Sentiment Scores by Model")
        analyses = db.get_sentiment_analyses()
        
        if analyses:
            df = pd.DataFrame(analyses)
            
            # Group by model and calculate average sentiment
            model_sentiment = df.groupby('model_name')['sentiment_score'].mean().reset_index()
            
            # Create a bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=model_sentiment, x='model_name', y='sentiment_score', ax=ax)
            ax.set_title('Average Sentiment Score by Model')
            ax.set_ylabel('Average Sentiment Score')
            ax.set_xlabel('Model')
            st.pyplot(fig)
            
            # Display raw data
            with st.expander("View Raw Data"):
                st.dataframe(df)
        else:
            st.info("No sentiment analyses available yet.")


if __name__ == "__main__":
    main()