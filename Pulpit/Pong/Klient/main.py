import sys
import pong
import stoly
from PyQt5.QtWidgets import QApplication, QWidget,  QLineEdit, QMessageBox, QPushButton, QHBoxLayout, QLabel, QGridLayout
from PyQt5.QtGui import QIcon
from network import Network
import traceback


class EkranLogowania(QWidget):

    def __init__(self, parent=None, styleSheet = ""):
        super().__init__(parent)
        self.serwer = Network()
        self.setStyleSheet(styleSheet)
        self.interfejs()
        #self.serwer.słuchaj()


    def interfejs(self):
        
        etykieta_login = QLabel("Login:", self)
        etykieta_hasło = QLabel("Hasło:", self)
        self.login = QLineEdit()
        self.login.setToolTip("Tutaj wpisz swój login")
        self.haslo = QLineEdit()
        self.haslo.setEchoMode(QLineEdit.Password)
        self.haslo.setToolTip("Tutaj wpisz swoje hasło")
        zalogujBtn = QPushButton("Zaloguj", self)
        zarejestrujBtn = QPushButton("Zarejestruj", self)
        wyjscieBtn = QPushButton("Wyjście", self)
        wyjscieBtn.resize(wyjscieBtn.sizeHint())

        uklad = QGridLayout()
        uklad.addWidget(etykieta_login, 0, 0)
        uklad.addWidget(etykieta_hasło, 0, 1)
        uklad.addWidget(self.login, 1, 0)
        uklad.addWidget(self.haslo, 1, 1)

        uklad2 = QHBoxLayout()
        uklad2.addWidget(zalogujBtn)
        uklad2.addWidget(zarejestrujBtn)
 
        uklad.addLayout(uklad2, 2, 0, 1, 3)
        uklad.addWidget(wyjscieBtn, 3, 0, 1, 3)

        self.setLayout(uklad)

        wyjscieBtn.clicked.connect(self.akcja)
        zalogujBtn.clicked.connect(self.akcja)
        zarejestrujBtn.clicked.connect(self.akcja)


        self.login.setFocus()
        #self.setGeometry(20, 20, 300, 100)
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Pong by KK&AS")

        self.ekran_rejestracji = EkranRejestracji(self.serwer, styleSheet=self.styleSheet())
        #self.stoly = Stoły()

    def wyjscie(self):
        self.close()

    def closeEvent(self, event):

        odp = QMessageBox.question(self, 'Komunikat',"Czy na pewno chcesz wyjść?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def akcja(self):

        nadawca = self.sender()

        if nadawca.text() == "Wyjście":
            self.wyjscie()
        elif nadawca.text() == "Zarejestruj":
            self.ekran_rejestracji.show()
        else:
            try:
                login = self.login.text()
                haslo = self.haslo.text()

                if not login or not haslo:
                    raise ValueError('nie podano danych')
                    
                if nadawca.text() == "Zaloguj":
                    #TODO: Łączenie z serwerem, serwer łączy się z bazą danych i odsyła wiadomość czy jest taki login i czy pasuje hasło
                    odp = self.serwer.wyślij(f"zaloguj_{login}_{haslo}").split("_")
                    print(odp)
                    if len(odp) > 1:
                        ekran_stołów = stoly.EkranStolow(self.serwer,login, parent_window = self, styleSheet = self.styleSheet())
                        ekran_stołów.show()
                        self.hide()
                        #pong.start(1200,780,300,30)
                        
                    #self.hide()
                    #self.ekran_stołów.show()
                
    
            except:
                traceback.print_exc()
                QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)

#################################################################################

class EkranRejestracji(QWidget):

    def __init__(self, serwer,  parent=None, styleSheet = ""):
        super().__init__(parent)
        self.interfejs()
        self.serwer = serwer
        self.setStyleSheet(styleSheet)


    def interfejs(self):
        etykieta_login = QLabel("Login:", self)
        etykieta_hasło = QLabel("Hasło:", self)
        etykieta_hasło_powtórz = QLabel("Powtórz hasło:", self)

        self.login = QLineEdit()
        self.haslo = QLineEdit()
        self.haslo_powtórz = QLineEdit()
        self.haslo.setEchoMode(QLineEdit.Password)
        self.haslo_powtórz.setEchoMode(QLineEdit.Password)

        OKBtn = QPushButton("OK", self)
        wyjscieBtn = QPushButton("Wyjście", self)
        wyjscieBtn.resize(wyjscieBtn.sizeHint())

        uklad = QGridLayout()
        uklad.addWidget(etykieta_login, 0, 0)
        uklad.addWidget(etykieta_hasło, 1, 0)
        uklad.addWidget(etykieta_hasło_powtórz, 2, 0)
        uklad.addWidget(self.login, 0, 1)
        uklad.addWidget(self.haslo, 1, 1)
        uklad.addWidget(self.haslo_powtórz,2,1)
        uklad.addWidget(OKBtn, 3,1)
        uklad.addWidget(wyjscieBtn, 3, 0)

        self.setLayout(uklad)

        wyjscieBtn.clicked.connect(self.akcja)
        OKBtn.clicked.connect(self.akcja)
       
        self.login.setFocus()
        #self.setGeometry(20, 20, 300, 100)
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Pong by KK&AS")

    def wyjscie(self):
        self.close()

    def closeEvent(self, event):

        odp = QMessageBox.question(self, 'Komunikat',"Czy na pewno chcesz wyjść?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def akcja(self):
        import traceback
        nadawca = self.sender()

        if nadawca.text() == "Wyjście":
            self.wyjscie()
        else:
            try:
                login = self.login.text()
                haslo = self.haslo.text()
                haslo_powtorz = self.haslo_powtórz.text()


                if not login or not haslo or haslo != haslo_powtorz:
                    raise ValueError('złe dane')
                    
                if nadawca.text() == "OK":
                    #TODO: Łączenie z serwerem, serwer łączy się z bazą danych i odsyła wiadomość czy jest taki login i czy pasuje hasło
                    self.serwer.wyślij(f"zarejestruj_{login}_{haslo}").split("_")
                    self.hide()

            except:
                traceback.print_exc()
                QMessageBox.warning(self, "Błąd", "Błędne dane", QMessageBox.Ok)
        
###################################################################################################

def uruchom():
    app = QApplication(sys.argv)
    stylesheet = None
    try:
        stylesheet = open("style.qss", "r").read()
    except:
        pass
    okno = EkranLogowania(styleSheet=stylesheet)
    okno.show()
    app.exec_()

if __name__ == '__main__':
    uruchom()
 