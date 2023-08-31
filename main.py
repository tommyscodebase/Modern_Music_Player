import os.path
import random
import time

from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl, QTimer
from music import Ui_MusicApp
import songs


class AdvancedMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Initial Position of the window
        self.initialPosition = self.pos()

        # Globals
        global stopped
        global looped
        global is_shuffled

        stopped = False
        looped = False
        is_shuffled = False

        # Create the player object
        self.player = QMediaPlayer()
        self.current_volume = 50

        # Slider Timer
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)

        # Connections
        # Default Page
        self.music_slider.sliderMoved[int].connect(
            lambda: self.player.setPosition(self.music_slider.value())
        )
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.pause_and_unpause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.next_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.loop_one_btn.clicked.connect(self.loop_one_song)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_playlist)
        self.delete_selected_btn.clicked.connect(self.remove_selected_song)
        self.delete_all_songs_btn.clicked.connect(self.remove_all_songs)

        self.show()

        def moveApp(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.initialPosition)
                self.initialPosition = event.globalPos()
                event.accept()

        self.title_frame.mouseMoveEvent = moveApp

    # Function to handle mouse position
    def mousePressEvent(self, event):
        self.initialPosition = event.globalPos()

    def move_slider(self):
        if stopped:
            return
        else:
            # Update the slider
            if self.player.state() == QMediaPlayer.PlayingState:
                self.music_slider.setMinimum(0)
                self.music_slider.setMaximum(self.player.duration())
                slider_position = self.player.position()
                self.music_slider.setValue(slider_position)

                current_time = time.strftime("%H:%M:%S", time.localtime(self.player.position() / 1000))
                song_duration = time.strftime("%H:%M:%S", time.localtime(self.player.duration() / 1000))
                self.time_label.setText(f"{current_time} / {song_duration}")

    # Add Songs to the app
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, caption='Add Songs', directory=':\\',
            filter='Supported Files (*.mp3;*.mpeg;*.ogg;*.m4a;*.MP3;*.wma;*.acc;*.amr)'
        )
        if files:
            for file in files:
                songs.current_song_list.append(file)
                self.loaded_songs_listWidget.addItem(
                    QListWidgetItem(
                        QIcon(':/img/utils/images/MusicListItem.png'),
                        os.path.basename(file)
                    )
                )

    # Play song
    def play_song(self):
        try:
            global stopped
            stopped = False
            current_selection = self.loaded_songs_listWidget.currentRow()
            current_song = songs.current_song_list[current_selection]

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Playing song error: {e}")

    # Pause and Unpause
    def pause_and_unpause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    # Stop Song
    def stop_song(self):
        try:
            self.player.stop()
            self.music_slider.setValue(0)
            self.time_label.setText(f'00:00:00 / 00:00:00')
            self.current_song_name.setText(f'Song name goes here')
            self.current_song_path.setText(f'Song path goes here')
        except Exception as e:
            print(f"Stopping song error: {e}")

    # Default next: song goes to the next in the queue
    def default_next(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]
            current_song_index = songs.current_song_list.index(current_song_url)
            if current_song_index + 1 == len(songs.current_song_list):
                next_index = 0
            else:
                next_index = current_song_index + 1
            current_song = songs.current_song_list[next_index]
            self.loaded_songs_listWidget.setCurrentRow(next_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Default next error: {e}")

    # Next function for looped songs
    def looped_next(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]
            current_song_index = songs.current_song_list.index(current_song_url)
            current_song = songs.current_song_list[current_song_index]
            self.loaded_songs_listWidget.setCurrentRow(current_song_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Looped next error: {e}")

    # Next function for shuffled songs
    def shuffled_next(self):
        try:
            song_index = random.randint(0, len(songs.current_song_list))
            current_song = songs.current_song_list[song_index]
            self.loaded_songs_listWidget.setCurrentRow(song_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Shuffled next error: {e}")

    # Next Song function
    def next_song(self):
        global looped
        global is_shuffled

        if is_shuffled:
            self.shuffled_next()
        elif looped:
            self.looped_next()
        else:
            self.default_next()

    # Default next: song goes to the next in the queue
    def previous_song(self):
        try:
            current_media = self.player.media()
            current_song_url = current_media.canonicalUrl().path()[1:]
            current_song_index = songs.current_song_list.index(current_song_url)
            if current_song_index == 0:
                previous_index = len(songs.current_song_list) - 1
            else:
                previous_index = current_song_index - 1
            current_song = songs.current_song_list[previous_index]
            self.loaded_songs_listWidget.setCurrentRow(previous_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name.setText(f'{os.path.basename(current_song)}')
            self.current_song_path.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Default next error: {e}")

    # Function to loop the song
    def loop_one_song(self):
        try:
            global is_shuffled
            global looped

            if not looped:
                looped = True
                self.shuffle_songs_btn.setEnabled(False)
            else:
                looped = False
                self.shuffle_songs_btn.setEnabled(True)
        except Exception as e:
            print(f"Looping song error: {e}")

    # Function to loop the song
    def shuffle_playlist(self):
        try:
            global is_shuffled
            global looped

            if not is_shuffled:
                is_shuffled = True
                self.loop_one_btn.setEnabled(False)
            else:
                is_shuffled = False
                self.loop_one_btn.setEnabled(True)
        except Exception as e:
            print(f"Looping song error: {e}")

    # Remove selected song
    def remove_selected_song(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove selected song',
                    'Playlist is empty'
                )
                return
            current_index = self.loaded_songs_listWidget.currentRow()
            self.loaded_songs_listWidget.takeItem(current_index)
            songs.current_song_list.pop(current_index)
        except Exception as e:
            print(f"Remove selected song error: {e}")

    # Remove all songs
    def remove_all_songs(self):
        try:
            if self.loaded_songs_listWidget.count() == 0:
                QMessageBox.information(
                    self, 'Remove selected song',
                    'Playlist is empty'
                )
                return
            question = QMessageBox.question(
                self, 'Remove all songs',
                'This action will remove all songs from the list and it cannot be reversed.\n'
                'Continue?',
                QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel
            )
            if question == QMessageBox.Yes:
                self.stop_song()
                self.loaded_songs_listWidget.clear()
                songs.current_song_list.clear()
        except Exception as e:
            print(f"Remove selected song error: {e}")
