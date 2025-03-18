# Drake Lyrics Sentiment Feedback App

A Streamlit application for collecting human feedback on Drake lyrics sentiment analysis.

## Features

- View Drake songs and their sentiment analysis results
- Provide feedback on sentiment analysis accuracy
- Explore sentiment distribution and trends
- Compare different sentiment analysis models

## Requirements

- Python 3.7+
- Streamlit 1.24.0+
- Pandas 1.3.0+
- NumPy 1.20.0+
- Matplotlib 3.4.0+
- Seaborn 0.11.0+

## Local Development Setup

1. Clone this repository
```bash
git clone https://github.com/yourusername/drake-sentiment-feedback-app.git
cd drake-sentiment-feedback-app
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the app
```bash
streamlit run streamlit_app.py
```

## Deployment on Streamlit Community Cloud

1. Push this repository to your GitHub account
2. Visit [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Sign in with GitHub
4. Click "New app"
5. Select this repository, branch, and file path to streamlit_app.py
6. Click "Deploy"

## Data Storage

The app uses SQLite for data storage with the following tables:
- `songs`: Store information about Drake songs
- `sentiment_analysis`: Store sentiment analysis results
- `sentiment_qa`: Store human feedback on sentiment analysis

## License

MIT
