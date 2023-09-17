import os.path
import random
import time

from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QUrl, QTimer

from db_functions import add_song_to_database_table, create_database_or_database_table, \
    fetch_all_songs_from_database_table, delete_song_from_database_table, delete_all_songs_from_database_table
from music import Ui_MusicApp
import songs


def create_db_dir():
    os.makedirs('.dbs', exist_ok=True)


class AdvancedMusicPlayer(QMainWindow, Ui_MusicApp):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.setupUi(self)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Initial Position of the window
        self.initialPosition = self.pos()

        # Database Stuff
        create_db_dir()
        create_database_or_database_table('favourites')
        self.load_favourites_into_app()

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
        self.player.mediaStatusChanged.connect(self.song_finished)
        # Default Page
        self.music_slider.sliderMoved[int].connect(
            lambda: self.player.setPosition(self.music_slider.value())
        )
        self.volume_dial.valueChanged.connect(lambda: self.volume_changed())
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

        self.song_list_btn.clicked.connect(self.switch_to_songs_tab)
        self.playlists_btn.clicked.connect(self.switch_to_playlist_tab)
        self.favourites_btn.clicked.connect(self.switch_to_favourites_tab)

        self.add_to_fav_btn.clicked.connect(self.add_song_to_favourites)
        self.delete_selected_favourite_btn.clicked.connect(self.remove_song_from_favourites)
        self.delete_all_favourites_btn.clicked.connect(self.remove_all_songs_from_favourites)

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

    # Function to determine the end of the song
    def song_finished(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song()

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
            if self.stackedWidget.currentIndex() == 0:
                current_selection = self.loaded_songs_listWidget.currentRow()
                current_song = songs.current_song_list[current_selection]
            elif self.stackedWidget.currentIndex() == 2:
                current_selection = self.favourites_listWidget.currentRow()
                current_song = songs.favourites_songs_list[current_selection]

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
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                current_song_index = songs.current_song_list.index(current_song_url)
                if current_song_index + 1 == len(songs.current_song_list):
                    next_index = 0
                else:
                    next_index = current_song_index + 1
                current_song = songs.current_song_list[next_index]
                self.loaded_songs_listWidget.setCurrentRow(next_index)
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                current_song_index = songs.favourites_songs_list.index(current_song_url)
                if current_song_index + 1 == len(songs.favourites_songs_list):
                    next_index = 0
                else:
                    next_index = current_song_index + 1
                current_song = songs.favourites_songs_list[next_index]
                self.favourites_listWidget.setCurrentRow(next_index)

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
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                current_song_index = songs.current_song_list.index(current_song_url)
                current_song = songs.current_song_list[current_song_index]
                self.loaded_songs_listWidget.setCurrentRow(current_song_index)
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                current_song_index = songs.favourites_songs_list.index(current_song_url)
                current_song = songs.favourites_songs_list[current_song_index]
                self.favourites_listWidget.setCurrentRow(current_song_index)

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
            if self.stackedWidget.currentIndex() == 0:
                song_index = random.randint(0, len(songs.current_song_list))
                current_song = songs.current_song_list[song_index]
                self.loaded_songs_listWidget.setCurrentRow(song_index)
            elif self.stackedWidget.currentIndex() == 2:
                song_index = random.randint(0, len(songs.favourites_songs_list))
                current_song = songs.favourites_songs_list[song_index]
                self.favourites_listWidget.setCurrentRow(song_index)

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
            if self.stackedWidget.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                current_song_index = songs.current_song_list.index(current_song_url)
                if current_song_index == 0:
                    previous_index = len(songs.current_song_list) - 1
                else:
                    previous_index = current_song_index - 1
                current_song = songs.current_song_list[previous_index]
                self.loaded_songs_listWidget.setCurrentRow(previous_index)
            elif self.stackedWidget.currentIndex() == 2:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().path()[1:]
                current_song_index = songs.favourites_songs_list.index(current_song_url)
                if current_song_index == 0:
                    previous_index = len(songs.favourites_songs_list) - 1
                else:
                    previous_index = current_song_index - 1
                current_song = songs.favourites_songs_list[previous_index]
                self.favourites_listWidget.setCurrentRow(previous_index)

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

    # Function to change the volume
    def volume_changed(self):
        try:
            self.current_volume = self.volume_dial.value()
            self.player.setVolume(self.current_volume)
        except Exception as e:
            print(f"Volume change error: {e}")

    # Switch to Favourites tab
    def switch_to_favourites_tab(self):
        self.stackedWidget.setCurrentIndex(2)

    # Switch to Song List tab
    def switch_to_songs_tab(self):
        self.stackedWidget.setCurrentIndex(0)

    # Switch to Song List tab
    def switch_to_playlist_tab(self):
        self.stackedWidget.setCurrentIndex(1)

    # FAVOURITE LIST FUNCTIONS
    # Load favourite songs
    def load_favourites_into_app(self):
        favourite_songs = fetch_all_songs_from_database_table('favourites')
        songs.favourites_songs_list.clear()
        self.favourites_listWidget.clear()

        for favourite in favourite_songs:
            songs.favourites_songs_list.append(favourite)
            self.favourites_listWidget.addItem(
                QListWidgetItem(
                    QIcon(':/img/utils/images/like.png'),
                    os.path.basename(favourite)
                )
            )

    # Add song to favourites
    def add_song_to_favourites(self):
        current_index = self.loaded_songs_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Add Songs to Favourites',
                'Select a song to add to favourites'
            )
            return
        try:
            song = songs.current_song_list[current_index]
            add_song_to_database_table(song=f"{song}", table='favourites')
            # QMessageBox.information(
            #     self, 'Add Songs to Favourites',
            #     f'{os.path.basename(song)} has been added to favourites'
            # )
            self.load_favourites_into_app()
        except Exception as e:
            print(f"Adding song to favourites error: {e}")

    # Remove song from favourites
    def remove_song_from_favourites(self):
        if self.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self, 'Remove song from Favourites',
                'Favourites list is empty.'
            )
            return
        current_index = self.favourites_listWidget.currentRow()
        if current_index is None:
            QMessageBox.information(
                self, 'Remove song from Favourites',
                'Select a song to remove from Favourites'
            )
        try:
            song = songs.favourites_songs_list[current_index]
            delete_song_from_database_table(song=f"{song}", table='favourites')
            self.load_favourites_into_app()
        except Exception as e:
            print(f"Removing from favourites error: {e}")

    # Remove all songs from favourites
    def remove_all_songs_from_favourites(self):
        if self.favourites_listWidget.count() == 0:
            QMessageBox.information(
                self, 'Remove all songs from Favourites',
                'Favourites list is empty.'
            )
            return
        question = QMessageBox.question(
            self, 'Remove all songs from Favourites',
            'This action will remove all songs from Favourites and it cannot be reversed.\n'
            'Continue?',
            QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel
        )
        if question == QMessageBox.Yes:
            try:
                delete_all_songs_from_database_table('favourites')
                self.load_favourites_into_app()
            except Exception as e:
                print(f"Removing all songs from favourites error: {e}")
