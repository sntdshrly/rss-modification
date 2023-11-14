from flask import Flask, request, render_template, jsonify
import feedparser
from textblob import TextBlob
from collections import Counter
import os
import json

app = Flask(__name__)

# Penyimpanan sementara untuk RSS feed, trending keywords, dan inbox
rss_feeds = []
search_history = Counter()
inbox = []

# Membaca data inbox dari file jika ada
inbox_file_path = 'inbox.json'
if os.path.exists(inbox_file_path):
    with open(inbox_file_path, 'r') as f:
        inbox = json.load(f)

def save_inbox_to_file():
    # Menyimpan data inbox ke file JSON
    with open(inbox_file_path, 'w') as f:
        json.dump(inbox, f)

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
    return render_template('index_combined.html')

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

        # Tambahkan berita ke inbox jika belum ada
        if entry.link not in [item['link'] for item in inbox]:
            inbox.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.published,
                'category': category,
                'read': False  # Menandai bahwa berita belum terbaca
            })

    # Catat kata kunci dalam history trending
    search_history.update([keyword])

    # Simpan perubahan di inbox ke file
    save_inbox_to_file()

    # Ambil trending kata
    trending_keywords = search_history.most_common(5)

    # Respons dalam bentuk JSON
    response = {
        'news': categorized_data,
        'trending_keywords': trending_keywords
    }

    return jsonify(response)

@app.route('/inbox', methods=['GET'])
def get_inbox():
    # Menampilkan data inbox
    return jsonify({'inbox': inbox})

@app.route('/mark_as_read/<string:link>', methods=['PUT'])
def mark_as_read(link):
    # Menandai berita dalam inbox sebagai sudah terbaca
    for item in inbox:
        if item['link'] == link:
            item['read'] = True
            break

    # Simpan perubahan di inbox ke file
    save_inbox_to_file()

    return jsonify({'message': 'Berita ditandai sebagai sudah terbaca'})

if __name__ == '__main__':
    app.run(debug=True)