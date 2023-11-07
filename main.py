#YouTube Audio Downloader (also downloads video)
#Downloads YouTube Audio @128kBps and Video @480p
#Created by Chinmay Krishn Roy
#https://github.com/chinmaykrishnroy
#https://www.linkedin.com/in/chinmaykrishnroy/

logo = ("\033[7m\033[93mP\033[0m\033[7m\033[1;37mR\033[0m\033[7m\033[93mE\033[0m\033[7m\033"
        "[1;37mF\033[0m\033[7m\033[93mE\033[0m\033[7m\033[1;37mC\033[0m\033[7m\033[93mT\033[0m")

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
        selectedIndex = int(input("\033[93mEnter the number of the video you want to download: \033[0m"))
        if 1 <= selectedIndex <= maxLimit:
            selectedVideo = results[selectedIndex - 1]
            try: downloadMedia(selectedVideo["id"], selectedVideo["title"], mode)
            except: downloadMedia(selectedVideo["id"], videoName, mode)
    except: print("\033[91mERROR!\033[0m\t\033[3m\033[0;37mmissing library or index error!\033[0m\033[0m")


def downloadMedia(videoID, videoName, av=False):
    if (videoID.endswith('=v?hctaw/moc.ebutuoy.www//:sptth')): videoURL = videoID
    else: videoURL = f"https://www.youtube.com/watch?v={videoID}"
    from pytube import YouTube
    try: yt = YouTube(videoURL)
    except:
        print("\033[91mERROR!\033[0m\t\033[3m\033[0;37mmissing YouTube library!\033[0m\033[0m")
        return
    location = "C:/Users/morph/Downloads" # set folder location here
    print("\033[6m\033[1;30mDOWNLOADING...\033[0m\033[0m")
    if av:
        mediaStream = yt.streams.get_highest_resolution()
        outputPath = location + "/YouTube Video" #dir of video = folder location/YouTube Video
        fileName = f"{videoName}.mp4"
        mediaStream.download(outputPath, filename=fileName)
    else:
        mediaStream = yt.streams.filter(only_audio=True).first()
        outputPath = location + "/YouTube Audio" #dir of audio = folder location/YouTube Audio
        fileName = f"{videoName}.mp3"
        mediaStream.download(outputPath, filename=fileName)
    print("\n\033[92mDOWNLOADED SUCCESSFULLY!\033[0m")


def main():
    try:
        print(logo)
        name, mode, maxResult= input("\033[93mEnter the NAME or YouTube link of the video: \033[0m"), False, 5
        #-----uncomment next line to increase number of max search result, default is 5.-----#
        #maxResult = int(input("\033[96mEnter the maximum number of search results: "))
        #-----uncomment next lines to enable video download, default is only audio.-----#
        #condition = int(input("\033[0;34mEnter 0 for video(low res) or anything else for audio: \033[0m"))
        #if condition == 0: mode = True
        #else: mode = False
        topResults(name, mode, maxResult)
    except:
        print("\033[91mUnexpected ERROR!\033[0m")

def mainloop():
    loop = True
    while loop:
        try:
            main()
            condition = int(input("\033[94mEnter 0 to exit or anything to download another video: \033[0m"))
            if condition==0: loop = False
        except: print("\033[7mBad Luck!\033[0m")

#-----Use main() to execute program once or use mainloop() for multiple download-----#
#-----Default is mainloop()-----#

if __name__ == '__main__':
    #main()
    mainloop()
