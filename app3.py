from flask import Flask, request, render_template, jsonify
import feedparser
from textblob import TextBlob

app = Flask(__name__)

# Penyimpanan sementara untuk RSS feed
rss_feeds = []

def categorize_news(entry):
    # Analisis sentimen menggunakan TextBlob
    blob = TextBlob(entry.title)
    sentiment_score = blob.sentiment.polarity

    # Kategorisasi berita berdasarkan sentimen
    if sentiment_score > 0.2:
        return 'Positif'
    elif sentiment_score < -0.2:
        return 'Negatif'
    else:
        return 'Netral'

@app.route('/')
def index():
    return render_template('index_categorize.html')

@app.route('/news', methods=['GET'])
def get_news():
    # URL RSS feed portal berita
    rss_url = 'http://rss.cnn.com/rss/edition_technology.rss'

    # Baca RSS feed
    feed = feedparser.parse(rss_url)

    # Kategorisasi berita
    categorized_data = []
    for entry in feed.entries:
        category = categorize_news(entry)
        categorized_data.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'category': category
        })

    # Respons dalam bentuk JSON
    response = {
        'news': categorized_data
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
