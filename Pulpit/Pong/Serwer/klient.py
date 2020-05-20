class Klient:
    def __init__(self, połączenie, serwer):
        self.połączenie = połączenie
        self.serwer = serwer

    def wyślij(self, wiadomość):
        self.połączenie.send(str.encode(wiadomość))

    def rozłącz(self, wiadomość="SerwerZakończyłPołączenie"):
        self.wyślij(wiadomość)
        self.połączenie.close()
        self.serwer.klienci.remove(self)