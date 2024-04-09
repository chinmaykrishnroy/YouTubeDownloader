# YouTube Audio Downloader (also downloads video)
# Downloads YouTube Audio @128kBps and Video @480p
# Created by Chinmay Krishn Roy
# https://github.com/chinmaykrishnroy
# https://www.linkedin.com/in/chinmaykrishnroy/

invalidFilenameChars = ['|', '"', "'", ':', '*', '?', '\\', '/', '<', '>']
logo = ("\033[7m\033[93mP\033[0m\033[7m\033[1;37mR\033[0m\033[7m\033[93mE\033[0m\033[7m\033"
        "[1;37mF\033[0m\033[7m\033[93mE\033[0m\033[7m\033[1;37mC\033[0m\033[7m\033[93mT\033[0m")


def validFileName(fileName, invalidASCII):
    invalidCharIndex = []
    for i in range(len(invalidASCII)):
        for j in range(len(fileName)):
            if fileName[j] == invalidASCII[i]: invalidCharIndex.append(j)
    if len(invalidCharIndex) == 0: return fileName
    invalidCharIndex.sort()
    if len(fileName[:invalidCharIndex[0]].strip()): return fileName[:invalidCharIndex[0]].strip()
    else: return ''.join(list(filter(lambda x: fileName.index(x) not in invalidCharIndex, fileName)))


def topResults(videoName, mode=False, maxLimit=5):
    tryURL = videoName.strip()[::-1]
    if (tryURL.endswith('=v?hctaw/moc.ebutuoy.www//:sptth')):
        try: downloadMedia(videoName, tryURL[0:10], mode)
        except: print("\033[91mERROR!\033[0m\t\033[3m\033[0;37minvalid link\033[0m\033[0m")
        return
    try:
        from youtubesearchpython import VideosSearch
        try: videosSearch = VideosSearch(videoName, limit=maxLimit)
        except:
            print("\033[91mERROR!\033[0m\t\033[3m\033[0;37mmissing video_search library!\033[0m\033[0m")
            return
        results = videosSearch.result()["result"]
        if not len(results):
            print("\033[0;31mnot found any search result!\033[0m\033[0m")
            return
        for i, video in enumerate(results, 1):
            print(f"\033[1m{i}\033[0m. \033[95m{video['title']}\033[0m - {video['link']}")
        selectedIndex = 1 #int(input("\033[93mEnter the number of the video you want to download: \033[0m"))
        if 1 <= selectedIndex <= maxLimit:
            selectedVideo = results[selectedIndex - 1]
            mediaName = validFileName(selectedVideo["title"], invalidFilenameChars)
            try: downloadMedia(selectedVideo["id"], mediaName, mode)
            except: downloadMedia(selectedVideo["id"], selectedVideo["title"], mode)
        else: print("\033[91mNot a valid choice!\033[0m\033[0m")
    except: print("\r\033[91mERROR!\033[0m\t\033[3m\033[0;37mmissing library or index error!\033[0m\033[0m")


def downloadMedia(videoID, videoName, av=False):
    if (videoID.endswith('=v?hctaw/moc.ebutuoy.www//:sptth')): videoURL = videoID
    else: videoURL = f"https://www.youtube.com/watch?v={videoID}"
    from pytube import YouTube
    try: yt = YouTube(videoURL)
    except:
        print("\033[91mERROR!\033[0m\t\033[3m\033[0;37mmissing YouTube library!\033[0m\033[0m")
        return
    import os, platform
    if platform.system() == "Windows": location = "C:/Users/%s/Downloads"%os.getlogin()
    elif os.getlogin()[::-1].endswith('_0u'): location = "/storage/emulated/0/Download"
    elif platform.system() == "Linux": location = "/home/%s/Downloads"%os.getlogin()
    elif platform.system() == "Darwin": location = "/Users/%s/Downloads"%os.getlogin()
    else: location = ""
    print("\r\033[6m\033[1;30mDOWNLOADING...\033[0m\033[0m", end='')
    if av:
        mediaStream = yt.streams.get_highest_resolution()
        outputPath = location + "/YouTube Video" # dir of video = folder location/YouTube Video
        fileName = f"{videoName}.mp4"
        mediaStream.download(outputPath, filename=fileName)
    else:
        mediaStream = yt.streams.filter(only_audio=True).first()
        outputPath = location + "/YouTube Audio" # dir of audio = folder location/YouTube Audio
        fileName = f"{videoName}.mp3"
        mediaStream.download(outputPath, filename=fileName)
    print("\r\033[92mDOWNLOADED SUCCESSFULLY!\033[0m")

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    if request.method == 'POST':
        data = request.form['input_data']
        checkbox_value = request.form.get('a_v', False)
        # Make mode=True for video downloading
        topResults(data, mode=checkbox_value, maxLimit=1)
        # Perform some processing with the data
        processed_data = data.upper()
        return render_template('downloaded.html')

if __name__ == '__main__':
    app.run(debug=False)

