from flask import Flask, request, jsonify
import feedparser

app = Flask(__name__)

# Penyimpanan sementara untuk RSS feed
rss_feeds = []

@app.route('/news', methods=['GET'])
def get_news():
    # Ambil parameter halaman dan ukuran halaman dari request
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    # URL RSS feed portal berita
    rss_url = 'http://rss.cnn.com/rss/edition_technology.rss'

    # Baca RSS feed
    feed = feedparser.parse(rss_url)

    # Hitung indeks awal dan akhir berdasarkan halaman dan ukuran halaman
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # Ambil data berita untuk halaman tertentu
    news_data = feed.entries[start_index:end_index]

    # Format data untuk respons
    formatted_data = []
    for entry in news_data:
        formatted_data.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published
        })

    # Respons dalam bentuk JSON
    response = {
        'page': page,
        'page_size': page_size,
        'total_results': len(feed.entries),
        'news': formatted_data
    }

    return jsonify(response)

@app.route('/add_feed', methods=['POST'])
def add_feed():
    data = request.get_json()
    new_feed = {
        'url': data.get('url'),
        'name': data.get('name')
    }
    rss_feeds.append(new_feed)
    return jsonify({'message': 'RSS feed added successfully'})

@app.route('/update_feed/<string:name>', methods=['PUT'])
def update_feed(name):
    print(f"Existing Feeds: {rss_feeds}")  # Add this line for debugging
    # Cari feed berdasarkan nama
    for feed in rss_feeds:
        if feed['name'] == name:
            data = request.get_json()
            feed['url'] = data.get('url', feed['url'])
            return jsonify({'message': 'RSS feed updated successfully'})
    return jsonify({'error': 'Feed not found'}), 404

@app.route('/delete_feed/<string:name>', methods=['DELETE'])
def delete_feed(name):
    print(f"Existing Feeds: {rss_feeds}")  # Add this line for debugging
    # Cari dan hapus feed berdasarkan nama
    for feed in rss_feeds:
        if feed['name'] == name:
            rss_feeds.remove(feed)
            return jsonify({'message': 'RSS feed deleted successfully'})
    return jsonify({'error': 'Feed not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
