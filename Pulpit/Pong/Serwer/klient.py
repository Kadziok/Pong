class Klient:
    """ Klasa odpowiadająca za obsługę klienta """
    def __init__(self, połączenie, serwer):
        """ 
        In
        ---
        połączenie - socket
        serwer - instancja serwera z którym połączył się klient
        """
        self.połączenie = połączenie
        self.serwer = serwer

    def wyślij(self, wiadomość):
        """ Wysyła wiadomość do klienta 
        In:
        ---
        wiadomość - treść wysłanej wiadomości
        """
        self.połączenie.send(str.encode(wiadomość))

    def rozłącz(self, wiadomość="SerwerZakończyłPołączenie"):
        """ Wysyła wiadomość o zakończeniu pracy serwera oraz kończy połączenie """
        self.wyślij(wiadomość)
        self.połączenie.close()
        self.serwer.klienci.remove(self)
