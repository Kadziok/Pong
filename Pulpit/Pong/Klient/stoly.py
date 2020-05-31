import sys
import traceback
import math
from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QIcon, QMovie, QBrush, QPainter, QPen, QFont
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QMessageBox,
                             QPushButton, QVBoxLayout, QWidget, QFrame)
from PyQt5.QtCore import Qt
from _thread import start_new_thread

import pong
from network import Network


class EkranStolow(QWidget):
    def __init__(self, serwer, mój_nick, parent=None, styleSheet = "", parent_window = None):
        super().__init__(parent)
        self.parent_window = parent_window
        self.setFixedSize(650, 500)
        self.serwer = serwer
        self.status = lambda x: "Oczekujący" if x == "1" else "Zajęty"
        self.mój_nick = mój_nick
        self.już_w_stole = False
        self.zalogowany = True
        self.setStyleSheet(styleSheet)
        self.numer_stołu = None
        self.interfejs()


    """        
    Tworzy interfejs okna
    """
    def interfejs(self):
        self.już_w_stole = False
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Pong by KK&AS")

        self.lista = QListWidget()
        self.lista.setFrameStyle(QFrame.NoFrame)
        self.lista.itemDoubleClicked.connect(self.dolacz)


        odp = self.serwer.wyślij("pobierzstoly").split("_")
        self.elementy = []
        if len(odp) > 1 and odp[1] != "":
            stoly = dict([i.split(":") for i in odp[1:]])

            self.elementy = [[f"Stół {i} \t| {self.status(stoly[i])}",
                    QColor('#7fc97f') if i == "1" else QColor('#A0A0A0')] for i in stoly]

        for e in self.elementy:
            i = QListWidgetItem(e[0])
            i.setBackground(e[1])
            self.lista.addItem(i)
            
        try:
            start_new_thread(EkranStolow.aktualizuj, (self,))
        except OSError:
            traceback.print_exc()

        uklad2 = QVBoxLayout()

        self.numer = QLineEdit()

        dodajBtn = QPushButton("Dodaj stół")
        dołączBtn = QPushButton("Dołącz do stołu")
        wylogujBtn = QPushButton("Wyloguj")

        try:
            ranking = int(self.serwer.wyślij("ranking"))
        except ValueError:
            ranking = -1

        if ranking == -1:
            witaj = QLabel(f"Witaj {self.mój_nick}!\nNie masz jeszcze pozycji rankingowej.")
        else:
            witaj = QLabel(f"Witaj {self.mój_nick}!\nAktualnie jesteś {ranking} w rankingu.")
        witaj.setStyleSheet("border: 1px solid #ccc;")

        uklad2.addWidget(witaj)
        uklad2.addWidget(wylogujBtn)

        przerwa = QLabel("\n"*5)
        przerwa.setStyleSheet("background-color: transparent;border: none;")

        uklad2.addWidget(przerwa)

        nowyLabel = QLabel("Utwórz nowy stół lub dołącz do istniejącego.")
        nowyLabel.setStyleSheet("border: 1px solid #ccc;")

        uklad2.addWidget(nowyLabel)
        uklad2.addWidget(self.numer)
        uklad2.addWidget(dodajBtn)
        uklad2.addWidget(dołączBtn)
        
        dodajBtn.clicked.connect(self.dodaj_stol)
        dołączBtn.clicked.connect(self.dolacz)
        wylogujBtn.clicked.connect(self.wyloguj)
        
        
        uklad = QGridLayout()
        uklad.addWidget(self.lista, 0, 0)
        uklad.addLayout(uklad2, 0, 1)

        self.setLayout(uklad)


    """
    Tworzy stół i uruchamia okno oczekiwania na przeciwnika
    """
    def dodaj_stol(self):
        if not self.już_w_stole:
            stol = self.numer.text()
            self.numer.setText("")
            
            try:
                numer = int(stol)
                self.numer_stołu = numer
                self.już_w_stole = True
            except ValueError:
                QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)
                return

            odp = self.serwer.wyślij(f"stworzstol_{numer}")

            if odp.startswith("stolistnieje"):
                QMessageBox.warning(self, "Błąd", f"Stol {numer} już istnieje.", QMessageBox.Ok)
            else:
                self._popframe = TranslucentWidget(self)
                self._popframe.move(0, 0)
                self._popframe.resize(self.width(), self.height())
                self._popflag = True
                self._popframe.show()
        else:
            QMessageBox.warning(self, "Błąd", "Jesteś już w stole", QMessageBox.Ok)

        
    """
    Dołącza do gry na już utworzonym stole
    """
    def dolacz(self, item):
        if not self.już_w_stole:
            numer = self.numer.text().strip()
            if numer == "":
                try:
                    numer = int(self.lista.selectedItems()[0].text().split(" ")[1])
                except IndexError:
                    return
            if numer != "":
                nick_przeciwnika = self.serwer.wyślij(f"nickprzeciwnika_{numer}_")
                
                odp = self.serwer.wyślij(f"dolacz_{numer}")

                self.już_w_stole = True

                self.zacznij_grę(nick_przeciwnika)
        else:
             QMessageBox.warning(self, "Błąd", "Jesteś już w stole", QMessageBox.Ok)


    """
    Pobiera i wyświetla listę aktualnie utworzonych stołów
    """
    def aktualizuj(self):
        while self.zalogowany:
            if not self.już_w_stole:
                odp = self.serwer.wyślij("pobierzstoly").split("_")
                nowe_elementy = []
                if len(odp) > 1 and odp[1] != "":
                    stoly = dict([i.split(":") for i in odp[1:]])

                    nowe_elementy = [[f"Stół {i} \t| {self.status(stoly[i])}",
                            QColor('#d32323') if stoly[i] == "1" else QColor('#A0A0A0')] for i in stoly]

                if nowe_elementy != self.elementy:
                    self.elementy = nowe_elementy
                    self.lista.clear()
                    for e in self.elementy:
                        i = QListWidgetItem(e[0])
                        i.setBackground(e[1])
                        self.lista.addItem(i)
            sleep(1)


    """
    Otwiera okno gry
    """
    def zacznij_grę(self, nick_przeciwnika):
        print("Rozpoczynanie gry")
        pong.start(800,400,300,30,self.serwer,self.mój_nick, nick_przeciwnika)


    """
    Wylogowuje (resetowanie danych użytkownika na serwerze) i pokazuje okno logowania
    """
    def wyloguj(self):
        if self.serwer.wyślij("wyloguj").startswith("wylogowano"):
            self.zalogowany = False
            self.hide()
            self.parent_window.show()
        else:
            QMessageBox.warning(self, "Błąd", "Wystąpił problem przy wylogowywaniu.\
                Spróbuj ponownie.", QMessageBox.Ok)


        


#############################################################################
"""
Okno do oczekiwania na dołącznie drugiego gracza
"""

class TranslucentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TranslucentWidget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.fillColor = QtGui.QColor(30, 30, 30, 120)
        self.penColor = QtGui.QColor("#333333")

        self.popup_fillColor = QtGui.QColor(240, 240, 240, 255)
        self.popup_penColor = QtGui.QColor(200, 200, 200, 255)

        self.close_btn = QtWidgets.QPushButton(self)
        self.close_btn.setText("Zrezygnuj z gry")

        s = self.parent().size()
        ow = int(s.width()/2)
        oh = int(s.height()/2)
        self.close_btn.move(ow - self.close_btn.size().width(), oh+70)


        font = QtGui.QFont()
        font.setPixelSize(18)
        font.setBold(True)
        self.close_btn.setFont(font)
        self.close_btn.clicked.connect(self.zamknij)

    """
    Rozmieszcza elementy okna
    """
    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(self.penColor)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

        qp.setPen(self.popup_penColor)
        qp.setBrush(self.popup_fillColor)
        popup_width = 300
        popup_height = 320
        ow = int(s.width()/2-popup_width/2)
        oh = int(s.height()/2-popup_height/2)
        qp.drawRoundedRect(ow, oh, popup_width, popup_height, 5, 5)


        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        qp.setFont(font)
        qp.setPen(QColor(70, 70, 70))
        tolw, tolh = 120, 80
        qp.drawText(ow + int(popup_width/2) - tolw, oh + int(popup_height/2) - tolh, "Oczekiwanie na przeciwnika.")

        qp.setPen(QPen(Qt.NoPen))
        for i in range(6):
            if (self.counter / 5) % 6 == i:
                qp.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
            else:
                qp.setBrush(QBrush(QColor(127, 127, 127)))
                qp.drawEllipse(
                    self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                    self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                    20, 20)

        qp.end()


    """
    Zamyka okno oczekiwania i ponownie uruchamia aktualizowanie listy stołów
    """
    def zamknij(self):
        odp = QMessageBox.question(self, 'Komunikat',"Czy na chcesz zrezygnować z gry?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp != QMessageBox.Yes:
            return
        self.parent().już_w_stole = False
        self.parent().serwer.wyślij("zrezygnuj")
        self.hide()

    def showEvent(self, event):     
        self.timer = self.startTimer(50)
        self.counter = 0


    """
    Sprawdza, czy drugi gracza dołączył do gry
    """
    def timerEvent(self, event):
        self.counter += 1
        self.update()
    
        if self.counter % 10 == 0:
            odp = self.parent().serwer.wyślij("czekam")
            if odp == "1":
                print("Zacznij grę")
                self.hide()
                nick_przeciwnika = self.parent().serwer.wyślij(f"nickprzeciwnika_{self.parent().numer_stołu}_")
                self.parent().zacznij_grę(nick_przeciwnika)


        if not self.isVisible():
            self.killTimer(self.timer)
            self.hide()


	
if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = EkranStolow(None, None)
    okno.show()
    app.exec_()
