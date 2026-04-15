import os
import sys
from pathlib import Path
from deepface import DeepFace

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import menu


class RecunoasterePhoto(QWidget):
    def __init__(self, parent=None):
        super(RecunoasterePhoto, self).__init__(parent)

        self.nume_fisier = ""

        self.setWindowTitle("Recunoaștere în poze")
        self.setWindowIcon(QIcon('face-scan.png'))

        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(10)
        layout_principal.setContentsMargins(16, 16, 16, 16)

        self.titlu = QLabel("Recunoaștere în poze")
        self.titlu.setObjectName('titlu')
        layout_principal.addWidget(self.titlu)

        self.btn_inapoi = QPushButton("← Înapoi la meniu")
        self.btn_inapoi.clicked.connect(self.intoarcere_la_meniu)
        layout_principal.addWidget(self.btn_inapoi)

        layout_continut = QHBoxLayout()
        layout_continut.setSpacing(12)

        # coloana stanga
        layout_stanga = QVBoxLayout()
        layout_stanga.setSpacing(8)
        layout_stanga.setAlignment(Qt.AlignTop)

        self.btn_incarcare = QPushButton("Încarcă poza")
        self.btn_incarcare.clicked.connect(self.deschide_selectarea_fisierului)
        layout_stanga.addWidget(self.btn_incarcare)

        self.btn_verificare = QPushButton("Verifică persoana")
        self.btn_verificare.setObjectName('btn_primary')
        self.btn_verificare.clicked.connect(self.recunoastere_foto)
        layout_stanga.addWidget(self.btn_verificare)

        # rezultat
        self.sectiune_rezultat = QFrame()
        self.sectiune_rezultat.setStyleSheet(
            "QFrame { background-color: #161618; border: 0.5px solid #2c2c2e; border-radius: 14px; }"
        )
        layout_rezultat = QVBoxLayout()
        layout_rezultat.setContentsMargins(14, 14, 14, 14)
        layout_rezultat.setSpacing(6)

        self.label_rezultat_titlu = QLabel("REZULTAT")
        self.label_rezultat_titlu.setObjectName('sectiune')
        layout_rezultat.addWidget(self.label_rezultat_titlu)

        self.label_nume = QLabel("—")
        self.label_nume.setStyleSheet("color: #bbb; font-size: 15px; font-weight: 500; border: none;")
        layout_rezultat.addWidget(self.label_nume)

        self.label_incredere = QLabel("")
        self.label_incredere.setObjectName('status_ok')
        layout_rezultat.addWidget(self.label_incredere)

        self.sectiune_rezultat.setLayout(layout_rezultat)
        layout_stanga.addWidget(self.sectiune_rezultat)

        layout_continut.addLayout(layout_stanga, 1)

        # coloana dreapta - poza
        layout_dreapta = QVBoxLayout()
        layout_dreapta.setSpacing(6)

        self.afisare_poza = QLabel()
        self.afisare_poza.setAlignment(Qt.AlignCenter)
        self.afisare_poza.setFixedSize(480, 360)
        self.afisare_poza.setStyleSheet(
            "background-color: #161618; border: 0.5px solid #2c2c2e; border-radius: 14px; color: #444; font-size: 12px;"
        )
        self.afisare_poza.setText("Nicio poză încărcată")
        layout_dreapta.addWidget(self.afisare_poza)

        self.label_fisier = QLabel("")
        self.label_fisier.setObjectName('status_ok')
        layout_dreapta.addWidget(self.label_fisier)

        layout_continut.addLayout(layout_dreapta, 2)
        layout_principal.addLayout(layout_continut)

        self.setLayout(layout_principal)

    def deschide_selectarea_fisierului(self):
        optiuni = QFileDialog.Options()
        optiuni |= QFileDialog.DontUseNativeDialog
        nume_fisier, _ = QFileDialog.getOpenFileName(
            self, "Selectați poza dorită", "",
            "Image files (*.jpg *.png)", options=optiuni
        )
        if nume_fisier:
            self.nume_fisier = nume_fisier
            self.label_fisier.setText(nume_fisier.split('/')[-1])
            self.afisare_fotografie()

    def recunoastere_foto(self):
        if not self.nume_fisier:
            return

        try:
            rezultate = DeepFace.find(
                img_path=self.nume_fisier,
                db_path='faces',
                model_name='VGG-Face',
                enforce_detection=False,
                silent=True
            )

            if rezultate and not rezultate[0].empty:
                identity = rezultate[0].iloc[0]['identity']
                nume = os.path.basename(identity).split('.')[0].replace('_', ' ')
                incredere = round((1 - rezultate[0].iloc[0]['distance']) * 100, 2)
                self.label_nume.setText(nume)
                self.label_incredere.setText(f"Încredere: {incredere}%")
            else:
                self.label_nume.setText("Neidentificat")
                self.label_incredere.setText("")

        except Exception as e:
            self.label_nume.setText("Eroare la recunoaștere.")
            print(e)

    def afisare_fotografie(self):
        pixmap = QPixmap(self.nume_fisier)
        pixmap = pixmap.scaled(480, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.afisare_poza.setPixmap(pixmap)
        self.afisare_poza.setText("")

    def intoarcere_la_meniu(self):
        self.meniu = menu.MeniuPrincipal()
        self.meniu.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('style.qss').read_text())
    fereastra = RecunoasterePhoto()
    fereastra.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()