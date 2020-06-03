import pygame
import pygame.locals
import network
from time import sleep

class Plansza(object):
    """ Klasa odpowiadająca za stworzenie planszy do gry """
    def __init__(self, szerokość, wysokość,tabela,r_kulki,serwer,mój_nick,nick_przeciwnika, gra):
        """
        In:
        ---
        szerokość, wysokość - rozmiar planszy
        tabela - rozmiar tabeli z boku
        r_kulki - promień piłki
        server - instacja serwera (Network)
        mój_nick - nick gracza
        nick_przecinika - nick przeciwnika gracza
        gra - instancja stowroznej gry (PongGame)
        """
        self.tabela = tabela
        self.szerokość = szerokość
        self.wysokość = wysokość
        self.r_kulki = r_kulki
        self.serwer = serwer
        self.mój_nick = mój_nick
        self.nick_przeciwnika = nick_przeciwnika
        self.ekran = pygame.display.set_mode((szerokość+tabela, wysokość))
        self.gra = gra
        
        pygame.display.set_caption('Pong by KK&AS')

    def rysuj(self, *args):
        if not self.gra.koniec:
            tło = [255, 255, 255]
            self.ekran.fill(tło, (0,0, self.szerokość + self.r_kulki + 3, self.wysokość))
            self.ekran.fill((123,123,123), (self.szerokość + self.r_kulki + 8, 0,self.szerokość + self.tabela, self.wysokość))
            # aktualizuje pozycję dla wszystich dziedzicących po klasie Rysujące
            for drawable in args:
                drawable.aktualizacja(self.ekran)
            pygame.display.update()

class PongGame(object):
    """ Klasa odpowiadająca za stworzenie gry  w Ponga"""
    def __init__(self, szerokość, wysokość, tabela, r_kulki, serwer, mój_nick, nick_przeciwnika):
        pygame.init()
        print("Rozpoczęto grę")
        self.Plansza = Plansza(szerokość, wysokość,tabela,r_kulki,serwer,mój_nick,nick_przeciwnika, self)
        self.zegar = pygame.time.Clock()
        self.piłka = Piłeczka(serwer, r_kulki, r_kulki, szerokość/2, wysokość/2)
        self.player1 = Rakieta(szerokość=80, wysokość=20, x=szerokość/2 - 40, y=wysokość - 40, kolor=(0,0,0),szerokość_planszy=szerokość,r_kulki=r_kulki,nick = mój_nick,serwer = serwer)
        self.player2 = Rakieta(szerokość=80, wysokość=20, x=szerokość/2 - 40, y=40, kolor=(0, 0, 0),szerokość_planszy=szerokość,r_kulki=r_kulki,nick = nick_przeciwnika, serwer = serwer)
        self.przeciwnik = Przeciwnik(self.player2, self.piłka)
        self.sędzia = Sędzia(self.Plansza, self.piłka, self.player2, self.piłka)
        self.serwer = serwer 
        self.koniec = False
 

    def run(self):
        while not self.koniec and not self.handle_events():
            self.piłka.move(self.Plansza, self.player1, self.player2)
            self.Plansza.rysuj(self.piłka, self.player1, self.player2, self.sędzia)
            self.zegar.tick(10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                self.serwer.wyślij("zrezygnuj")
                print("Wciśnięto X")
                pygame.display.quit()
                return True

            if event.type == pygame.locals.MOUSEMOTION:
                    x, y = event.pos
                    self.player1.move(x)
    
    def zakończ(self):
        pygame.display.quit()


    @staticmethod
    def odbierz_wiadomosc(wiadomość, gra):
        """ Służy do odbierania wiadomości z serwera podczas włączonej gry """
        if wiadomość.startswith("ustaw"):
            x = int(wiadomość.split("_")[1])
            if x > 800:
                x = 800
            elif x < 0:
                x = 0
            #symetria!
            x = 754 - x
            gra.przeciwnik.rakieta.pozycja.x = x
        elif wiadomość.startswith("zmien.poz.pił"):
            poz = eval(wiadomość.split("_")[1])
            gra.piłka.pozycja.x = int(poz[0])
            gra.piłka.pozycja.y = int(poz[1])
            pnk = eval(wiadomość.split("_")[2])
            gra.sędzia.score = pnk
        elif wiadomość.find("wygral") >= 0:
            try:
                nick = wiadomość[wiadomość.index("wygral"):].split("_")[1]
            except:
                print(wiadomość)
                nick = "błąd"
            moj_font = pygame.font.SysFont('agencyfb',30)
            text = moj_font.render(f"Koniec gry. Wygrał gracz {nick}", True, (0, 0, 0))
            pozycja = text.get_rect()
            pozycja.center = 300, 200
            gra.Plansza.ekran.blit(text, pozycja)
            gra.koniec = True
            gra.zakończ()


class Przeciwnik(object):
    def __init__(self, rakieta, piłka):
        self.piłka = piłka
        self.rakieta = rakieta
    def move(self):
        x = self.piłka.pozycja.centerx
        self.rakieta.move(x)     


class Rysujące(object):
    def __init__(self, szerokość, wysokość, x, y, kolor):
        self.szerokość = szerokość
        self.wysokość = wysokość
        self.kolor = kolor
        self.ekran = pygame.Surface([szerokość, wysokość], pygame.SRCALPHA, 32).convert_alpha()
        self.pozycja = self.ekran.get_rect(x=x, y=y)

    def aktualizacja(self, ekran):
        ekran.blit(self.ekran, self.pozycja)
        

class Sędzia(Rysujące):
    """ Klasa aktualizująca wyniki w tabelce"""
    def __init__(self, Plansza, piłka, *args):
        self.piłka = piłka
        self.Plansza = Plansza
        self.rakiety = args
        self.score = [0, 0]

    def drukuj_tekst(self, ekran,  text, x, y):
        moj_font = pygame.font.SysFont('agencyfb',30)
        text = moj_font.render(text, True, (255, 255, 255))
        pozycja = text.get_rect()
        pozycja.center = x, y
        ekran.blit(text, pozycja)

    def aktualizacja(self, ekran):
        wysokość = self.Plansza.wysokość
        szerokość = self.Plansza.szerokość
        tabela = self.Plansza.tabela
       
        self.drukuj_tekst(ekran, f"{self.Plansza.mój_nick} {self.score[0]}", szerokość+tabela/2 , wysokość*0.05)
        self.drukuj_tekst(ekran, f"{self.Plansza.nick_przeciwnika} {self.score[1]}", szerokość+tabela/2 ,wysokość*0.1 )



class Rakieta(Rysujące):
    """ Klasa do obsługi rakietki na planszy"""
    def __init__(self, szerokość, wysokość, x, y, kolor,szerokość_planszy,r_kulki, nick, serwer):
        super(Rakieta, self).__init__(szerokość, wysokość, x, y, kolor)
        self.szerokość_planszy = szerokość_planszy
        self.r_kulki = r_kulki
        self.ekran.fill(kolor)
        self.nick = nick
        self.serwer = serwer
        
    def move(self, x, ustaw = False):
        if ustaw:
            self.pozycja.x = x
        delta = x - self.pozycja.x
        if self.pozycja.x + delta < self.szerokość_planszy + self.r_kulki - self.szerokość:
            self.pozycja.x += delta
        else:
            self.pozycja.x = self.szerokość_planszy + self.r_kulki + 4 - self.szerokość 
        self.serwer.wyślij(f"ustaw_{self.pozycja.x}_{self.pozycja.y}_{self.szerokość}_{self.wysokość}_")


class Piłeczka(Rysujące):
    """ Klasa do obsługi piłeczki na planszy """
    def __init__(self, serwer, szerokość, wysokość, x, y, kolor=(255, 0, 0), prędkość_x=1, prędkość_y=1):
        super(Piłeczka, self).__init__(szerokość, wysokość, x, y, kolor)
        pygame.draw.ellipse(self.ekran, self.kolor, [0, 0, self.szerokość, self.wysokość])
        self.prędkość_x = prędkość_x
        self.prędkość_y = prędkość_y
        self.start_x = x
        self.start_y = y
        self.serwer = serwer

    def move(self, Plansza, *args):
        self.serwer.wyślij(f"piłeczka_{Plansza.szerokość}_{Plansza.wysokość}_{self.szerokość}_{self.wysokość}_")
       
       


def start(szerokość, wysokość,tabela,r_kulki, serwer, mój_nick, nick_przeciwnika):
    """ Uruchamia grę """
    gra = PongGame(szerokość, wysokość,tabela,r_kulki, serwer, mój_nick, nick_przeciwnika)

    serwer.zakoncz_nasluchiwanie()
    serwer.słuchaj(PongGame.odbierz_wiadomosc, gra)

    gra.run()
    