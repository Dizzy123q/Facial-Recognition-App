import sys
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

import recognition
import photo_recognition
import add_to_database
import os
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class MeniuPrincipal(QDialog):
    def __init__(self, parent=None):
        super(MeniuPrincipal, self).__init__(parent)

        self.setWindowTitle("Facial recognition")
        self.setWindowIcon(QIcon('face-scan.png'))
        self.setFixedWidth(500)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setAlignment(Qt.AlignCenter)

        self.titlu = QLabel("Facial recognition")
        self.titlu.setObjectName('titlu')
        self.titlu.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.titlu)

        self.subtitlu = QLabel("Choose a mode")
        self.subtitlu.setObjectName('subtitlu')
        self.subtitlu.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitlu)

        layout.addSpacing(16)

        self.btn_video = QPushButton("Video recognition")
        self.btn_video.setObjectName('btn_primary')
        self.btn_video.clicked.connect(self.deschide_recunoasterea_video)
        layout.addWidget(self.btn_video)

        self.btn_foto = QPushButton("Photo recognition")
        self.btn_foto.clicked.connect(self.deschide_recunoasterea_photo)
        layout.addWidget(self.btn_foto)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #2c2c2e;")
        layout.addWidget(separator)

        self.btn_adaugare = QPushButton("Add person to database")
        self.btn_adaugare.clicked.connect(self.deschide_meniul_de_adaugare_in_baza_de_date)
        layout.addWidget(self.btn_adaugare)

        self.setLayout(layout)

    def deschide_recunoasterea_photo(self):
        self.recunoastere_faciala_in_poze = photo_recognition.RecunoasterePhoto()
        self.recunoastere_faciala_in_poze.show()
        self.close()

    def deschide_recunoasterea_video(self):
        self.recunoastere_faciala_in_timp_real = recognition.FaceRecognitionWebcam()
        self.recunoastere_faciala_in_timp_real.show()
        self.close()

    def deschide_meniul_de_adaugare_in_baza_de_date(self):
        self.adaugare_in_baza_de_date = add_to_database.AdaugaInBazaDeDate()
        self.adaugare_in_baza_de_date.show()
        self.close()


def main():
    aplicatie = QApplication(sys.argv)
    aplicatie.setFont(QFont("Arial", 13))
    aplicatie.setStyleSheet(Path('style.qss').read_text())
    meniu = MeniuPrincipal()
    meniu.show()
    sys.exit(aplicatie.exec_())


if __name__ == '__main__':
    main()