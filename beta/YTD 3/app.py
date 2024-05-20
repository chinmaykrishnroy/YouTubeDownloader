import os, re, requests
from flask import Flask, render_template, request, redirect, url_for, flash
from pytube import YouTube, Search
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def format_readable_number(number):
    if number < 1_000: return str(number)
    elif number < 1_000_000: return f"{number / 1_000:.1f}K".rstrip('0').rstrip('.')
    elif number < 1_000_000_000: return f"{number / 1_000_000:.1f}M".rstrip('0').rstrip('.')
    else: return f"{number / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')

def time_ago(timestamp):
    now = datetime.now()
    past = timestamp
    time_difference = now - past
    if time_difference < timedelta(minutes=1):
        return "just now"
    elif time_difference < timedelta(hours=1):
        minutes = time_difference.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif time_difference < timedelta(days=1):
        hours = time_difference.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif time_difference < timedelta(weeks=1):
        days = time_difference.days
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif time_difference < timedelta(days=30):
        weeks = time_difference.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif time_difference < timedelta(days=365):
        months = time_difference.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = time_difference.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"

def get_channel_thumbnail(channel_id):
    try:
        channel_url = f'https://www.youtube.com/channel/{channel_id}'
        response = requests.get(channel_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        thumbnail_url = soup.find('meta', property='og:image')['content']
        print("Channel Thumbnail URL:", thumbnail_url)
        return thumbnail_url
    except Exception as e:
        print(f"Error occurred while fetching channel thumbnail: {e}")
        return "assets/video-thumbnail"
    
def get_video_description(video_id):
    try:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(video_url)
        video_html = yt.watch_html
        description = re.search(r'"description":\s*"(.*?)",', video_html).group(1)
        description = description.encode().decode('unicode-escape')
        return description
    except Exception as e:
        print(f"Error occurred while fetching description: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    search_results = Search(query).results
    videos = []
    for result in search_results:
        videos.append({
            'id': result.video_id,
            'title': result.title,
            'description': result.description,
            'thumbnail': result.thumbnail_url,
            'view' : format_readable_number(result.views),
            'channel' : result.author,
            'channel_img' : get_channel_thumbnail(result.channel_id),
            'age' : time_ago(result.publish_date),
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

import webbrowser
if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
