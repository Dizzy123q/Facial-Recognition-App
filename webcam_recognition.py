import sys
import cv2
import os
import numpy as np
import math
from pathlib import Path

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import menu
import dialog


def calculare_incredere_detectare(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'


class FaceRecognitionWebcam(QWidget):
    def __init__(self, parent=None):
        super(FaceRecognitionWebcam, self).__init__(parent)

        titlu = "Recunoastere faciala a infractorilor"
        self.setWindowTitle(titlu)
        self.setWindowIcon(QIcon('face-scan.png'))

        Layout_vertical = QVBoxLayout()
        Layout_vertical_2 = QVBoxLayout()
        Layout_orizontal = QHBoxLayout()
        Layout_orizontal_2 = QHBoxLayout()
        Layout_orizontal_final = QHBoxLayout()

        self.btn_menu = QPushButton("Inapoi la meniu", self)
        self.btn_menu.clicked.connect(self.inapoi_la_meniu)
        Layout_vertical.addWidget(self.btn_menu)

        self.afisare_stream_video = QLabel(self)
        self.afisare_stream_video.setFixedWidth(640)
        self.afisare_stream_video.setFixedHeight(480)
        self.afisare_stream_video.setStyleSheet("border: 2px solid white")
        Layout_vertical.addWidget(self.afisare_stream_video)

        self.coordonatele_fetei_persoanei_din_video = []
        self.codari_fete_variabila_utilitara= []
        self.codarile_fetelor_cunoscute = []
        self.numele_fetelor_cunoscute = []
        self.procesarea_frameului_curent = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reimprospateaza_stramul_camerei)

        self.buton_pornire_camera = QPushButton("Porneste Camera", self)
        self.buton_pornire_camera.clicked.connect(self.porneste_camera)
        Layout_orizontal.addWidget(self.buton_pornire_camera)
        
        self.buton_pornire_recunoastere_faciala = QPushButton("Porneste recunoasterea faciala", self)
        self.buton_pornire_recunoastere_faciala.clicked.connect(self.porneste_recunoasterea_faciala)
        Layout_orizontal.addWidget(self.buton_pornire_recunoastere_faciala)
        
        self.buton_opreste_camera = QPushButton("Opreste Camera", self)
        self.buton_opreste_camera.clicked.connect(self.opreste_camera)
        Layout_orizontal_2.addWidget(self.buton_opreste_camera)

        self.buton_reimprospatare_recunoastere_faciala = QPushButton("Reporneste Scanarea", self)
        self.buton_reimprospatare_recunoastere_faciala.clicked.connect(self.reimprospateaza_stramul_camerei)
        Layout_orizontal_2.addWidget(self.buton_reimprospatare_recunoastere_faciala)

        Layout_vertical.addLayout(Layout_orizontal)
        Layout_vertical.addLayout(Layout_orizontal_2)

        self.titlu = QLabel(f"Persoane in baza de date")
        font = QFont("Arial", 12)
        self.titlu.setFont(font)
        Layout_vertical_2.addWidget(self.titlu)

        self.listView = QListView()
        self.model = QStandardItemModel()
        self.listView.setModel(self.model)
        Layout_vertical_2.addWidget(self.listView)

        self.buton_bifare_evidentiere_fata = QCheckBox("Evidentiaza fata")
        self.buton_bifare_evidentiere_fata.setChecked(False)
        Layout_vertical_2.addWidget(self.buton_bifare_evidentiere_fata)

        self.buton_bifare_evidentiere_nume = QCheckBox("Afiseaza numele")
        self.buton_bifare_evidentiere_nume.setChecked(False)
        Layout_vertical_2.addWidget(self.buton_bifare_evidentiere_nume)

        Layout_orizontal_final.addLayout(Layout_vertical)
        Layout_orizontal_final.addLayout(Layout_vertical_2)

        self.setLayout(Layout_orizontal_final)

        for nume in self.numele_fetelor_cunoscute:
            nume = nume.split('.')[-2]
            nume = nume.replace('_', ' ')
            self.model.appendRow(QStandardItem(nume))

        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def porneste_camera(self):
        self.capture = cv2.VideoCapture(0)
        

        if not self.capture.isOpened():
            print('Nu a fost gasita nici o sursa video.')
            return

        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        
    def porneste_recunoasterea_faciala(self):
        self.timer.start(5) 


    def reimprospateaza_stramul_camerei(self):
        self.valoare, self.frame = self.capture.read()
        if not self.valoare:
            return
        self.frame = cv2.flip(self.frame, 1)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        if self.procesarea_frameului_curent:
            frame_micsorat = cv2.resize(self.frame, (0,0), fx =0.25, fy=0.25)
            rgb_frame_micsorat = frame_micsorat[:, :, ::-1]

            self.coordonatele_fetei_persoanei_din_video = face_recognition.face_locations(rgb_frame_micsorat)
            self.codari_fete_variabila_utilitara = face_recognition.face_encodings(rgb_frame_micsorat, self.coordonatele_fetei_persoanei_din_video)

            self.numele_fetelor=[]

            for codare_fata_variabila_utilitata in self.codari_fete_variabila_utilitara:
                potriviri = face_recognition.compare_faces(self.codarile_fetelor_cunoscute, codare_fata_variabila_utilitata)
                self.nume = "Necunoscut"
                incredere = '???'

                face_distances = face_recognition.face_distance(self.codarile_fetelor_cunoscute, codare_fata_variabila_utilitata)
                best_match_index = np.argmin(face_distances)

                if potriviri[best_match_index]:
                    self.nume = self.numele_fetelor_cunoscute[best_match_index]
                    incredere = calculare_incredere_detectare(face_distances[best_match_index])

                self.numele_fetelor.append(f'{self.nume.replace("_", " ")} ({incredere})')

        self.procesarea_frameului_curent = not self.procesarea_frameului_curent

        for(sus, dreapta, jos, stanga), self.nume in zip(self.coordonatele_fetei_persoanei_din_video, self.numele_fetelor):
            sus *= 4
            dreapta *= 4
            jos *= 4
            stanga *= 4

            if self.buton_bifare_evidentiere_fata.isChecked():
                cv2.rectangle(self.frame, (stanga, sus), (dreapta, jos), (0, 0, 255), 2)
                cv2.rectangle(self.frame, (stanga, jos - 35), (dreapta, jos), (0, 0, 255), cv2.FILLED)

            if self.buton_bifare_evidentiere_nume.isChecked():
                cv2.putText(self.frame, self.nume.split('.')[-3], (stanga + 6 , jos - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            self.fereastra_dialog = dialog.MyDialog(self.nume)

            if isinstance(self.fereastra_dialog, dialog.MyDialog):
                self.fereastra_dialog.show()
                self.timer.stop()

        stream_video = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], self.frame.strides[0], QImage.Format_RGB888)
        self.afisare_stream_video.setPixmap(QPixmap.fromImage(stream_video))


    def opreste_camera(self):
        self.timer.stop()

    def camera_update(self):
        self.timer.start(5)

    def inapoi_la_meniu(self):
        self.fereastra_meniu = menu.MeniuPrincipal()
        self.fereastra_meniu.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('style.qss').read_text())
    win = FaceRecognitionWebcam()
    win.show()
    sys.exit((app.exec_()))

if __name__ == '__main__':
    main()
