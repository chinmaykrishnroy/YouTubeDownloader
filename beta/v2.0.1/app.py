from flask import Flask, render_template, request, redirect, url_for, flash
from youtubesearchpython import VideosSearch
from pytube import YouTube
import os
import platform

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# List of invalid filename characters
invalidFilenameChars = ['|', '"', "'", ':', '*', '?', '\\', '/', '<', '>']

def validFileName(fileName, invalidASCII):
    invalidCharIndex = []
    for i in range(len(invalidASCII)):
        for j in range(len(fileName)):
            if fileName[j] == invalidASCII[i]:
                invalidCharIndex.append(j)
    if len(invalidCharIndex) == 0:
        return fileName
    invalidCharIndex.sort()
    if len(fileName[:invalidCharIndex[0]].strip()):
        return fileName[:invalidCharIndex[0]].strip()
    else:
        return ''.join(list(filter(lambda x: fileName.index(x) not in invalidCharIndex, fileName)))

def downloadMedia(videoID, videoName, av=False):
    videoURL = f"https://www.youtube.com/watch?v={videoID}"
    try:
        yt = YouTube(videoURL)
    except:
        flash("Error: Missing YouTube library or invalid URL!", "danger")
        return None

    if platform.system() == "Windows":
        location = "C:/Users/%s/Downloads" % os.getlogin()
    elif os.getlogin()[::-1].endswith('_0u'):
        location = "/storage/emulated/0/Download"
    elif platform.system() == "Linux":
        location = "/home/%s/Downloads" % os.getlogin()
    elif platform.system() == "Darwin":
        location = "/Users/%s/Downloads" % os.getlogin()
    else:
        location = ""

    if av:
        mediaStream = yt.streams.get_highest_resolution()
        outputPath = os.path.join(location, "YouTube Video")
        fileName = f"{videoName}.mp4"
    else:
        mediaStream = yt.streams.filter(only_audio=True).first()
        outputPath = os.path.join(location, "YouTube Audio")
        fileName = f"{videoName}.mp3"

    os.makedirs(outputPath, exist_ok=True)
    mediaStream.download(outputPath, filename=fileName)
    return os.path.join(outputPath, fileName)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    max_results = int(request.form.get('max_results', 5))
    
    try:
        videos_search = VideosSearch(query, limit=max_results)
        results = videos_search.result()["result"]
        if not results:
            flash("No search results found!", "warning")
            return redirect(url_for('index'))
        
        return render_template('results.html', results=results)
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/download', methods=['POST'])
def download():
    video_id = request.form['video_id']
    video_title = request.form['video_title']
    download_type = request.form['download_type']
    sanitized_title = validFileName(video_title, invalidFilenameChars)
    av = True if download_type == 'video' else False
    
    file_path = downloadMedia(video_id, sanitized_title, av)
    if file_path:
        flash(f"Downloaded successfully: {file_path}", "success")
    else:
        flash("Failed to download the media.", "danger")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
