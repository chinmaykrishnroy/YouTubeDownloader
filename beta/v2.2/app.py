from flask import Flask, render_template, request, redirect, url_for, flash
from pytube import YouTube, Search
from youtubesearchpython import VideosSearch
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    # search_results = Search(query).results
    videos_search = VideosSearch(query, limit=20)
    results = videos_search.result()
    videos = []
    if 'result' in results:
        for video in results['result']:
            videos.append({
                'id': video['id'],
                'title': video['title'][:40],
                'description': video['descriptionSnippet'][0]['text'],
                'thumbnail': video['thumbnails'][0]['url']
            })
    return render_template('results.html', videos=videos)

@app.route('/download/<video_id>/<format>')
def download(video_id, format):
    yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
    if format == 'video':
        stream = yt.streams.get_highest_resolution()
        filename = stream.download(output_path='downloads')
        flash(f'Video downloaded: {filename}', 'success')
    elif format == 'audio':
        stream = yt.streams.filter(only_audio=True).first()
        filename = stream.download(output_path='downloads')
        base, ext = os.path.splitext(filename)
        new_file = base + '.mp3'
        os.rename(filename, new_file)
        flash(f'Audio downloaded: {new_file}', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
