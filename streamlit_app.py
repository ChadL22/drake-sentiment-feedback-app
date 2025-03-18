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
class SentimentDatabase:
    def __init__(self, db_path="data/drake_sentiment.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self._initialize_db()
    
    def _get_connection(self):
        """Get a database connection"""
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
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
        conn.close()
        
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
    
    def save_sentiment_analysis(self, song_id, model_name, sentiment_score, sentiment_category=None):
        """Save a sentiment analysis to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO sentiment_analysis (song_id, model_name, sentiment_score, sentiment_category)
        VALUES (?, ?, ?, ?)
        ''', (song_id, model_name, sentiment_score, sentiment_category))
        
        sa_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return sa_id

# Initialize sample data
def initialize_sample_data(db):
    """Initialize sample data if database is empty"""
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
                 "Yeah, they wishin' and wishin' and wishin' and wishin'\nThey wishin' on me, yeah\nI been movin' calm, don't start no trouble with me\nTryna keep it peaceful is a struggle for me\nDon't pull up at 6 AM to cuddle with me\nYou know how I like it when you lovin' on me\nI don't wanna die for them