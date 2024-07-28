from PyQt5.QtCore import QCoreApplication
from PyQt5.QtMultimedia import QSound
import sys

def play_boss():
    app = QCoreApplication(sys.argv)
    sound = QSound("res/boss_time.wav")
    sound.play()
    sys.exit(app.exec_())

if __name__ == '__main__':
    play_boss()