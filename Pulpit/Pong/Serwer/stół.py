class Stół:
    stoły = {}

    def __init__(self, numer, gracz, nick_gracza):
        self.numer = numer
        self.gracz1 = gracz
        self.gracz2 = None
        self.gracz1_nick = nick_gracza
        self.gracz2_nick = None
        self.czeka = True
        self.pozycja1 = (0,0)
        self.pozycja2 = (0,0)
        self.piłeczka_pozycja = (400,200)
        self.prędkość_x = 1.0
        self.prędkość_y = 1.0
        self.piłeczka_pozycja_startowa = (400,200)
        self.score = [0, 0]

    def dołącz(self, gracz):
        self.gracz2 = gracz
        self.czeka = False

    def przeciwnik(self, gracz):
        if self.gracz1 == gracz:
            return self.gracz2
        else:
            return self.gracz1

    def wyślij(self, gracz):
        pass

    def pozycja(self, gracz, pozycja):
        if self.gracz1 == gracz:
            self.pozycja1 = pozycja
            return self.pozycja2
        else:
            self.pozycja2 = pozycja
            return self.pozycja1