import sys
import cv2
import os
from pathlib import Path
from deepface import DeepFace

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import menu
import dialog


class FaceRecognitionWebcam(QWidget):
    def __init__(self, parent=None):
        super(FaceRecognitionWebcam, self).__init__(parent)

        self.setWindowTitle("Recunoaștere facială")
        self.setWindowIcon(QIcon('face-scan.png'))

        self.frame = None
        self.capture = None
        self.overlay_nume = None
        self.overlay_box = None
        self.numele_fetelor_cunoscute = []

        self.timer_camera = QTimer(self)
        self.timer_camera.timeout.connect(self.afisare_camera)

        self.timer_recunoastere = QTimer(self)
        self.timer_recunoastere.timeout.connect(self.recunoastere_faciala)

        layout_principal = QHBoxLayout()
        layout_principal.setSpacing(12)
        layout_principal.setContentsMargins(16, 16, 16, 16)

        # coloana stanga - camera
        layout_stanga = QVBoxLayout()
        layout_stanga.setSpacing(8)

        self.titlu = QLabel("Recunoaștere facială")
        self.titlu.setObjectName('titlu')
        layout_stanga.addWidget(self.titlu)

        self.btn_inapoi = QPushButton("← Înapoi la meniu")
        self.btn_inapoi.clicked.connect(self.inapoi_la_meniu)
        layout_stanga.addWidget(self.btn_inapoi)

        self.afisare_stream_video = QLabel()
        self.afisare_stream_video.setFixedSize(640, 480)
        self.afisare_stream_video.setAlignment(Qt.AlignCenter)
        self.afisare_stream_video.setStyleSheet(
            "background-color: #161618; border: 0.5px solid #2c2c2e; border-radius: 14px; color: #444; font-size: 12px;"
        )
        self.afisare_stream_video.setText("Camera oprită")
        layout_stanga.addWidget(self.afisare_stream_video)

        self.label_status = QLabel("Camera inactivă")
        self.label_status.setObjectName('status_ok')
        layout_stanga.addWidget(self.label_status)

        row1 = QHBoxLayout()
        self.btn_pornire_camera = QPushButton("Pornește camera")
        self.btn_pornire_camera.setObjectName('btn_primary')
        self.btn_pornire_camera.clicked.connect(self.porneste_camera)
        row1.addWidget(self.btn_pornire_camera)

        self.btn_pornire_recunoastere = QPushButton("Pornește recunoașterea")
        self.btn_pornire_recunoastere.clicked.connect(self.porneste_recunoasterea_faciala)
        row1.addWidget(self.btn_pornire_recunoastere)
        layout_stanga.addLayout(row1)

        row2 = QHBoxLayout()
        self.btn_oprire_camera = QPushButton("Oprește camera")
        self.btn_oprire_camera.clicked.connect(self.opreste_camera)
        row2.addWidget(self.btn_oprire_camera)

        self.btn_repornire = QPushButton("Repornește scanarea")
        self.btn_repornire.clicked.connect(self.porneste_recunoasterea_faciala)
        row2.addWidget(self.btn_repornire)
        layout_stanga.addLayout(row2)

        layout_principal.addLayout(layout_stanga)

        # coloana dreapta - baza de date + overlay
        layout_dreapta = QVBoxLayout()
        layout_dreapta.setSpacing(8)
        layout_dreapta.setAlignment(Qt.AlignTop)

        self.label_baza_date = QLabel("BAZĂ DE DATE")
        self.label_baza_date.setObjectName('sectiune')
        layout_dreapta.addWidget(self.label_baza_date)

        self.listView = QListView()
        self.listView.setFixedWidth(200)
        self.model = QStandardItemModel()
        self.listView.setModel(self.model)
        self.listView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout_dreapta.addWidget(self.listView)

        self.label_overlay = QLabel("OVERLAY")
        self.label_overlay.setObjectName('sectiune')
        layout_dreapta.addWidget(self.label_overlay)

        self.sectiune_overlay = QFrame()
        self.sectiune_overlay.setStyleSheet(
            "QFrame { background-color: #161618; border: 0.5px solid #2c2c2e; border-radius: 14px; }"
        )
        layout_overlay = QVBoxLayout()
        layout_overlay.setContentsMargins(14, 14, 14, 14)
        layout_overlay.setSpacing(8)

        self.check_fata = QCheckBox("Evidențiază fața")
        self.check_fata.setChecked(False)
        layout_overlay.addWidget(self.check_fata)

        self.check_nume = QCheckBox("Afișează numele")
        self.check_nume.setChecked(False)
        layout_overlay.addWidget(self.check_nume)

        self.sectiune_overlay.setLayout(layout_overlay)
        layout_dreapta.addWidget(self.sectiune_overlay)

        layout_principal.addLayout(layout_dreapta)
        self.setLayout(layout_principal)

        for imagine in os.listdir('faces'):
            nume = imagine.split('.')[0].replace('_', ' ')
            self.numele_fetelor_cunoscute.append(imagine)
            self.model.appendRow(QStandardItem(nume))

    def porneste_camera(self):
        self.capture = cv2.VideoCapture(0)

        if not self.capture.isOpened():
            self.label_status.setText("Camera nu a fost găsită.")
            return

        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.afisare_stream_video.setText("")
        self.label_status.setText("Camera activă")
        self.timer_camera.start(30)

    def porneste_recunoasterea_faciala(self):
        self.overlay_nume = None
        self.overlay_box = None
        self.label_status.setText("Scanare activă...")
        self.timer_recunoastere.start(1000)

    def afisare_camera(self):
        if self.capture is None:
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        self.frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        if self.overlay_box and self.check_fata.isChecked():
            x, y, w, h = self.overlay_box
            cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (200, 200, 200), 2)

        if self.overlay_nume and self.overlay_box and self.check_nume.isChecked():
            x, y, w, h = self.overlay_box
            cv2.putText(frame_rgb, self.overlay_nume,
                        (x, y - 10 if y > 20 else y + h + 20),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (200, 200, 200), 1)

        stream_video = QImage(frame_rgb, frame_rgb.shape[1], frame_rgb.shape[0],
                              frame_rgb.strides[0], QImage.Format_RGB888)
        self.afisare_stream_video.setPixmap(QPixmap.fromImage(stream_video))

    def recunoastere_faciala(self):
        if self.frame is None:
            return

        try:
            rezultate = DeepFace.find(
                img_path=self.frame,
                db_path='faces',
                model_name='VGG-Face',
                enforce_detection=False,
                silent=True
            )

            if rezultate and not rezultate[0].empty:
                row = rezultate[0].iloc[0]
                identity = row['identity']
                nume_detectat = os.path.basename(identity).split('.')[0]
                incredere = round((1 - row['distance']) * 100, 2)
                nume_afisat = f"{nume_detectat.replace('_', ' ')} ({incredere}%)"

                if 'source_x' in row:
                    self.overlay_box = (
                        int(row['source_x']), int(row['source_y']),
                        int(row['source_w']), int(row['source_h'])
                    )

                self.overlay_nume = nume_afisat
                self.label_status.setText(f"Detectat: {nume_detectat.replace('_', ' ')}")
                self.timer_recunoastere.stop()

                self.fereastra_dialog = dialog.MyDialog(
                    f"{nume_detectat}.jpg {incredere}%"
                )
                self.fereastra_dialog.show()

        except Exception as e:
            print(e)

    def opreste_camera(self):
        self.timer_camera.stop()
        self.timer_recunoastere.stop()
        self.label_status.setText("Camera oprită")
        self.afisare_stream_video.setText("Camera oprită")
        self.afisare_stream_video.setPixmap(QPixmap())

    def inapoi_la_meniu(self):
        self.timer_camera.stop()
        self.timer_recunoastere.stop()
        self.fereastra_meniu = menu.MeniuPrincipal()
        self.fereastra_meniu.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('style.qss').read_text())
    win = FaceRecognitionWebcam()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()