from main import AdvancedMusicPlayer
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = AdvancedMusicPlayer()
sys.exit(app.exec())
