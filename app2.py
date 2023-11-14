from flask import Flask, request, render_template, jsonify
import feedparser
from collections import Counter
import re

app = Flask(__name__)

# Penyimpanan sementara untuk RSS feed dan trending kata
rss_feeds = []
search_history = Counter()

def highlight_keyword(text, keyword):
    # Membuat pola regex untuk pencarian kata kunci tanpa memperhatikan huruf besar/kecil
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    # Menandai (highlight) kata kunci dengan tag HTML
    highlighted_text = pattern.sub(lambda m: f'<span style="background-color: yellow;">{m.group()}</span>', text)
    return highlighted_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news', methods=['GET'])
def get_news():
    # Ambil parameter kata kunci dari request
    keyword = request.args.get('keyword', '')

    # URL RSS feed portal berita
    rss_url = 'http://rss.cnn.com/rss/edition_technology.rss'

    # Baca RSS feed
    feed = feedparser.parse(rss_url)

    # Cari kata kunci dalam judul berita
    highlighted_data = []
    for entry in feed.entries:
        title = highlight_keyword(entry.title, keyword)
        highlighted_data.append({
            'title': title,
            'link': entry.link,
            'published': entry.published
        })

    # Catat kata kunci dalam history trending
    search_history.update([keyword])

    # Ambil trending kata
    trending_keywords = search_history.most_common(5)

    # Respons dalam bentuk JSON
    response = {
        'news': highlighted_data,
        'trending_keywords': trending_keywords
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)