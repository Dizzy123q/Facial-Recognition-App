import os
import sys
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import menu


class AdaugaInBazaDeDate(QWidget):
    def __init__(self, parent=None):
        super(AdaugaInBazaDeDate, self).__init__(parent)

        self.nume_fisier_clasa = ""

        self.setWindowTitle("Add to database")
        self.setWindowIcon(QIcon('face-scan.png'))
        self.setFixedWidth(550)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        self.titlu = QLabel("Add to database")
        self.titlu.setObjectName('titlu')
        layout.addWidget(self.titlu)

        self.btn_inapoi = QPushButton("← Back to menu")
        self.btn_inapoi.clicked.connect(self.inapoi_la_meniu)
        layout.addWidget(self.btn_inapoi)

        # sectiune fotografie
        self.label_foto = QLabel("PHOTO")
        self.label_foto.setObjectName('sectiune')
        layout.addWidget(self.label_foto)

        self.sectiune_foto = QFrame()
        self.sectiune_foto.setStyleSheet(
            "QFrame { background-color: #161618; border: 0.5px solid #2c2c2e; border-radius: 14px; }"
        )
        layout_foto = QVBoxLayout()
        layout_foto.setContentsMargins(14, 14, 14, 14)
        layout_foto.setSpacing(10)

        self.eticheta_fisier = QLabel("No file selected")
        self.eticheta_fisier.setAlignment(Qt.AlignCenter)
        self.eticheta_fisier.setStyleSheet(
            "color: #555; font-size: 12px; border: 0.5px dashed #3a3a3c; border-radius: 12px; padding: 16px;"
        )
        layout_foto.addWidget(self.eticheta_fisier)

        self.btn_incarcare = QPushButton("Load photo")
        self.btn_incarcare.clicked.connect(self.deschide_selectarea_fisierului)
        layout_foto.addWidget(self.btn_incarcare)

        self.sectiune_foto.setLayout(layout_foto)
        layout.addWidget(self.sectiune_foto)

        # sectiune nume
        self.label_nume = QLabel("PERSON NAME")
        self.label_nume.setObjectName('sectiune')
        layout.addWidget(self.label_nume)

        self.sectiune_nume = QFrame()
        self.sectiune_nume.setStyleSheet(
            "QFrame { background-color: #161618; border: 0.5px solid #2c2c2e; border-radius: 14px; }"
        )
        layout_nume = QVBoxLayout()
        layout_nume.setContentsMargins(14, 14, 14, 14)
        layout_nume.setSpacing(10)

        row = QHBoxLayout()
        self.input_nume = QLineEdit()
        self.input_nume.setPlaceholderText("Ex: John Doe")
        row.addWidget(self.input_nume)

        self.btn_adauga = QPushButton("Add")
        self.btn_adauga.setObjectName('btn_primary')
        self.btn_adauga.setFixedWidth(120)
        self.btn_adauga.clicked.connect(self.adauga_in_baza_de_date)
        row.addWidget(self.btn_adauga)

        layout_nume.addLayout(row)

        self.label_status = QLabel("")
        self.label_status.setObjectName('status_ok')
        layout_nume.addWidget(self.label_status)

        self.sectiune_nume.setLayout(layout_nume)
        layout.addWidget(self.sectiune_nume)

        self.setLayout(layout)

    def deschide_selectarea_fisierului(self):
        optiuni = QFileDialog.Options()
        optiuni |= QFileDialog.DontUseNativeDialog
        nume_fisier, _ = QFileDialog.getOpenFileName(
            self, "Select the desired photo", "",
            "Image files (*.jpg *.png)", options=optiuni
        )
        if nume_fisier:
            self.nume_fisier_clasa = nume_fisier
            self.eticheta_fisier.setText(nume_fisier.split('/')[-1])
            self.eticheta_fisier.setStyleSheet(
                "color: #aaa; font-size: 12px; border: 0.5px dashed #3a3a3c; border-radius: 12px; padding: 16px;"
            )

    def adauga_in_baza_de_date(self):
        if not self.nume_fisier_clasa:
            self.label_status.setText("Please select a photo first.")
            return

        cale_fisier = self.nume_fisier_clasa
        numele_fisierului = cale_fisier.split('/')[-1]
        cale_de_salvare = "faces/"
        cale_cu_nume_fisier = cale_de_salvare + numele_fisierului

        try:
            os.replace(cale_fisier, cale_cu_nume_fisier)

            nume_nou = self.input_nume.text().strip().title().replace(" ", "_")
            if not nume_nou:
                self.label_status.setText("Please enter a name.")
                return

            os.rename(cale_cu_nume_fisier, cale_de_salvare + nume_nou + ".jpg")
            self.label_status.setText("Person added successfully.")

        except FileNotFoundError:
            self.label_status.setText("File not found.")
        except Exception as e:
            self.label_status.setText(f"Error: {e}")

    def inapoi_la_meniu(self):
        self.meniu = menu.MeniuPrincipal()
        self.meniu.show()
        self.close()


def main():
    aplicatie = QApplication(sys.argv)
    aplicatie.setStyleSheet(Path('style.qss').read_text())
    fereastra = AdaugaInBazaDeDate()
    fereastra.show()
    sys.exit(aplicatie.exec_())


if __name__ == '__main__':
    main()