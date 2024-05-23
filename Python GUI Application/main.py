import sys, os
import webbrowser
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import (Qt, QTimer, Slot, QPoint, QThread, Signal, Slot, 
    QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QFontMetrics
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QGridLayout, QFileDialog, QMessageBox
)
from youtubesearchpython import VideosSearch
from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable
import youtube_dl

class WorkerThread(QThread):
    taskFinished = Signal()

    def __init__(self, main_window, param):
        super().__init__()
        self.main_window = main_window
        self.param = param

    def run(self):
        # Call the long-running function of the MainWindow class
        self.main_window.search(self.param)
        self.taskFinished.emit()

class CircularLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)

    def paintEvent(self, event):
        if self.pixmap():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            path = QPainterPath()
            path.addEllipse(self.rect())
            painter.setClipPath(path)
            painter.drawPixmap(self.rect(), self.pixmap())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window properties
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(100, 100, 700, 510)
        self.setFixedSize(700, 510)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Variables to track mouse movements for dragging
        self.drag_start_position = None
        self.oldPos = self.pos()

        # Main container widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Set style sheet to remove border and padding
        self.setStyleSheet("border: none; padding: 0;")

        # Header
        self.header = QWidget()
        self.header.setStyleSheet("background-color: black;")
        self.header_layout = QHBoxLayout()
        self.header.setLayout(self.header_layout)
        
        # Logo as a QPushButton
        self.logo_button = QPushButton('YouTube')
        self.logo_button.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        self.logo_button.clicked.connect(self.open_youtube)
        self.header_layout.addWidget(self.logo_button)
        
        self.search_bar = QWidget()
        self.search_layout = QHBoxLayout()
        self.search_bar.setLayout(self.search_layout)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Enter Anything...')
        self.search_input.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;                       
            color: white;
            padding: 4px; border-radius: 2px; border: 1px solid #ccc;
        """)
        self.search_layout.addWidget(self.search_input)
        
        # Search button
        self.search_button = QPushButton('Search')
        self.search_button.setStyleSheet("""
            background-color: red; color: white; padding: 8px; border-radius: 4px;
            border: 1px;
        """)
        self.search_button.clicked.connect(self.search_handler)
        self.search_layout.addWidget(self.search_button)
        # Custom close button
        self.close_button = QPushButton()
        self.close_button.setStyleSheet("""
            background-color: grey; color: white; padding: 8px; border-radius: 4px;
            border: none;
        """)
        self.close_button.setIcon(QIcon("close_icon.png"))  # Set custom close button icon
        self.close_button.setFixedSize(32, 32)  # Set button size
        self.close_button.clicked.connect(self.close_window)  # Connect to close handler
        self.search_layout.addWidget(self.close_button)

        self.header_layout.addWidget(self.search_bar)
        
        self.layout.addWidget(self.header)

        self.initial_message_label = QLabel("\n\n\nSearch Video With\nName to Generate\nResponses")
        self.initial_message_label.setStyleSheet("""
            color: black;
            font: Montserrat;
            font-size: 32px;
            font-weight: bold;
            text-align: left;
            padding-left: 205px;
        """)
        self.initial_message_label.setAlignment(Qt.AlignLeft)
        
        # Create a layout to centralize the initial message label
        self.initial_message_layout = QVBoxLayout()
        self.initial_message_layout.addWidget(self.initial_message_label)
        self.initial_message_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(self.initial_message_layout)

        self.initial_message_animation = QPropertyAnimation(self.initial_message_label, b"geometry")
        self.initial_message_animation.setDuration(500)
        self.initial_message_animation.setStartValue(self.initial_message_label.geometry().translated(-self.width(), 0))
        self.initial_message_animation.setEndValue(self.initial_message_label.geometry())
        self.initial_message_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.sequential_animation = QSequentialAnimationGroup()
        self.sequential_animation.addAnimation(self.initial_message_animation)
        self.sequential_animation.start()

        self.loading_text = QLabel("\n\n\nLoading\nResults...")
        self.loading_text.setStyleSheet("""
            color: black;
            font: Montserrat;
            font-size: 32px;
            font-weight: bold;
            text-align: left;
        """)
        self.loading_text.setAlignment(Qt.AlignCenter)

        self.downloading_text = QLabel("\n\n\n\nDownloading...")
        self.downloading_text.setStyleSheet("""
            color: black;
            font: Montserrat;
            font-size: 32px;
            font-weight: bold;
            text-align: left;
        """)
        self.downloading_text.setAlignment(Qt.AlignCenter)

        self.downloaded_message = QLabel("\n\n\n\nDownloaded!", self)
        self.downloaded_message.setStyleSheet("""
            color: black;
            font: Montserrat;
            font-size: 32px;
            font-weight: bold;
            text-align: left;
        """)
        self.downloaded_message.setAlignment(Qt.AlignCenter)
        self.downloaded_message.setVisible(False)

        # Timer to hide the downloaded message
        self.download_timer = QTimer()
        self.download_timer.setSingleShot(True)
        self.download_timer.timeout.connect(self.hide_downloaded_message)
        # Hide the initial message initially
        self.loading(False)
        self.downloading_text.setVisible(False)

        # Video container
        self.videos = []
        self.video_container = QWidget()
        self.video_container_layout = QGridLayout()
        self.video_container.setLayout(self.video_container_layout)
        self.video_container_layout.addWidget(self.initial_message_label)
        self.layout.addWidget(self.loading_text)
        self.layout.addWidget(self.downloading_text)
        self.layout.addWidget(self.downloaded_message)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("QScrollBar::vertical { width: 2; }")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.video_container)
        self.layout.addWidget(self.scroll_area)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reset_placeholder)

        # Load initial video
        self.show_initial_message(True)

    def search(self, query):
        videos_search = VideosSearch(query, limit=20)
        self.hide_downloading_message()
        results = videos_search.result()
        self.videos = []
        if 'result' in results:
            for video in results['result']:
                try:
                    self.videos.append({
                        'id': video['id'],
                        'title': video['title'],
                        'thumbnail': video['thumbnails'][1]['url'],
                        'views' : video['viewCount']['short'],
                        'channel' : video['channel']['name'],
                        'channel_img' : video['channel']['thumbnails'][0]['url'],
                        'age' : video['publishedTime']
                    })
                except:
                    self.videos.append({
                        'id': video['id'],
                        'title': video['title'],
                        'thumbnail': video['thumbnails'][0]['url'],
                        'views' : video['viewCount']['short'],
                        'channel' : video['channel']['name'],
                        'channel_img' : video['channel']['thumbnails'][0]['url'],
                        'age' : video['publishedTime']
                    })
        self.reset_placeholder();
        return True
    
    def show_downloaded_message(self):
        self.video_container.setVisible(False)
        self.downloaded_message.setVisible(True)
        self.download_timer.start(5000)  # Show the message for 2 seconds

    def hide_downloaded_message(self):
        self.downloaded_message.setVisible(False)
        self.video_container.setVisible(True)

    def show_initial_message(self, show):
        self.initial_message_label.setVisible(show)

    def loading(self, show):
        self.loading_text.setVisible(show)
        if self.downloading_text.isVisible(): 
            self.downloading_text.setVisible(False)
        if self.downloaded_message.isVisible(): 
            self.downloaded_message.setVisible(False)

    def update_video_list(self):
        # Clear existing videos from the layout
        for i in reversed(range(self.video_container_layout.count())):
            widget_to_remove = self.video_container_layout.itemAt(i).widget()
            self.video_container_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        # Fetch and create video data asynchronously
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.create_video_widget, video): video for video in self.videos}
            for future in as_completed(futures):
                video_data = future.result()
                QTimer.singleShot(0, lambda v=video_data: self.add_video_to_layout(v))
        self.loading(False)

    @Slot()
    def add_video_to_layout(self, video_data):
        video = video_data['video']
        thumbnail_pixmap = video_data['thumbnail_pixmap']
        channel_thumbnail_pixmap = video_data['channel_thumbnail_pixmap']
        
        video_widget = QWidget()
        video_widget.setStyleSheet("border-bottom: none;")  # Remove border
        video_layout = QHBoxLayout()
        # video_layout.addStretch(1)  # Add a stretchable spacer item to push the thumbnail to the right
        video_widget.setLayout(video_layout)
        video_widget.setStyleSheet("border-bottom: 1px solid #ccc;")
        
        # Thumbnail as a QPushButton
        thumbnail_button = QPushButton()
        thumbnail_button.setFlat(True)
        thumbnail_button.setObjectName(video['id'])
        thumbnail_button.setIcon(QIcon(thumbnail_pixmap))
        thumbnail_button.setIconSize(thumbnail_pixmap.size())
        thumbnail_button.clicked.connect(self.thumbnail_handler)
        
        video_details = QWidget()
        video_details_layout = QVBoxLayout()
        video_details.setLayout(video_details_layout)
        video_details.setStyleSheet("border-bottom: none;")
        
        # Channel thumbnail
        channel_thumbnail_label = CircularLabel()
        channel_thumbnail_label.setPixmap(channel_thumbnail_pixmap)
        
        video_info = QWidget()
        video_info_layout = QVBoxLayout()
        video_info.setLayout(video_info_layout)
        
        video_title = QLabel(video['title'])
        video_title.setStyleSheet("font-weight: bold;")
        video_title = QLabel(video['title'])
        video_title.setStyleSheet("font-weight: bold;")
        video_title.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Align text to top left
        video_title.setWordWrap(True)  # Enable word wrap
        font_metrics = QFontMetrics(video_title.font())
        elided_text = font_metrics.elidedText(video['title'], Qt.ElideRight, video_title.width())
        video_title.setText(elided_text)
        
        channel_name = QLabel(video['channel'])
        views_age = f"{video['views']} • {video['age']}"
        views_label = QLabel(views_age)
        
        # Add video title, channel name, and views to the video_info_layout
        video_info_layout.addWidget(video_title)
        video_info_layout.addWidget(channel_name)
        video_info_layout.addWidget(views_label)
        
        video_details_layout.addWidget(channel_thumbnail_label)
        video_details_layout.addWidget(video_info)
        
        video_layout.addWidget(thumbnail_button)
        video_layout.addWidget(video_details)
        
        row = self.video_container_layout.rowCount()
        self.video_container_layout.addWidget(video_widget, row, 0)

    def create_video_widget(self, video):
        # Asynchronously download thumbnail
        def load_thumbnail(thumbnail_url):
            try:
                response = requests.get(thumbnail_url)
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                if pixmap.isNull():
                    pixmap = QPixmap("default_thumbnail.jpg")
                return pixmap.scaledToWidth(320, Qt.SmoothTransformation)
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
                return QPixmap("default_thumbnail.jpg")
        
        thumbnail_pixmap = load_thumbnail(video['thumbnail'])
        
        channel_thumbnail_pixmap = QPixmap()
        try:
            channel_thumbnail_response = requests.get(video['channel_img'])
            channel_thumbnail_pixmap.loadFromData(channel_thumbnail_response.content)
        except Exception as e:
            print(f"Error loading channel thumbnail: {e}")
        
        return {
            'video': video,
            'thumbnail_pixmap': thumbnail_pixmap,
            'channel_thumbnail_pixmap': channel_thumbnail_pixmap
        }


    def download(self, video_id):
        try:
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
            stream = yt.streams.get_highest_resolution()
            filename = stream.download(output_path=folder_path)
            print(f'Video downloaded: {filename}', 'success')
            self.hide_downloading_message()
            self.show_downloaded_message()
        except Exception as e:
            print(f'Error: {e}')
            QMessageBox.critical(None, "Download Error", f"An error occurred while downloading the video: {e}")
            self.download_with_youtube_dl(video_id)
    
    def download_with_youtube_dl(self,video_id):
        try:
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
            stream = yt.streams.get_highest_resolution()
            default_filename = stream.default_filename

            # Use QFileDialog to get save location and filename
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_path, _ = QFileDialog.getSaveFileName(None, "Save Video As", default_filename, "All Files (*);;MP4 Files (*.mp4)", options=options)

            if file_path:
                # Ensure the file path has the correct extension
                if not file_path.endswith('.mp4'):
                    file_path += '.mp4'

                ydl_opts = {
                    'outtmpl': file_path,
                    'format': 'bestvideo+bestaudio/best',
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
                print(f'Video downloaded: {file_path}', 'success')
            else:
                print('Download canceled by user')
        except Exception as e:
            print(f'Error with youtube-dl: {e}')
            self.hide_downloading_message()
            QMessageBox.critical(None, "Download Error", f"An error occurred while downloading the video: {e}")

    def open_youtube(self):
        webbrowser.open("https://www.youtube.com")

    def thumbnail_handler(self):
        thumbnail_button = self.sender()
        if thumbnail_button:
            video_id = thumbnail_button.objectName()
            print(f"Thumbnail clicked: {video_id}")
            self.show_downloading_message()
            self.download(video_id)

    def show_downloading_message(self):
        self.video_container.setVisible(False)
        self.downloading_text.setVisible(True)

    def hide_downloading_message(self):
        self.downloading_text.setVisible(False)
        self.video_container.setVisible(True)

    @Slot()
    def search_handler(self):
        search_text = self.search_input.text().strip()
        if search_text:
            # Hide initial message
            self.show_initial_message(False)

            # Show loading message
            self.loading(True)
            self.video_container.setVisible(False)

            self.worker_thread = WorkerThread(self, search_text)
            self.worker_thread.taskFinished.connect(self.seach_complete_handler)

            # Start the worker thread
            self.worker_thread.start()
        else:
            self.search_button.setStyleSheet("""
                background-color: red; color: white; padding: 8px; border-radius: 4px;
                border: 2px solid #ff0000;
                animation: shake 0.5s;
            """)
            self.search_input.setPlaceholderText("Can't do blank search!")
            self.timer.start(1000)
    
    @Slot()
    def seach_complete_handler(self):
        self.update_video_list()
        self.video_container.setVisible(True)
        self.search_input.clear()

    def reset_placeholder(self):
        self.search_button.setStyleSheet("""
            background-color: red; color: white; padding: 8px; border-radius: 4px;
            border: none;
        """)
        self.search_input.setPlaceholderText('Enter Anything...')
    
    def close_window(self):
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.pos() + delta)
            self.oldPos = event.globalPosition().toPoint()
    
    def mouseDoubleClickEvent(self, event):
        self.mousePressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
