import socket
import stół
import pygame
import pygame.locals
import klient
from _thread import *
import sys
import os



class Serwer:
    import os
    import socket
    from _thread import start_new_thread
    import mysql.connector
    import traceback


    def __init__(self, ip, port):
        import mysql.connector
        self.ip = ip
        self.port = 5555
        self.klienci = []
        self.włączony = True
        self.stoły = {}
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="server",
            passwd="zaq1@WSX",
            database="pong"
            )

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.s.bind((ip, port))
        except socket.error as e:
            str(e)


    def wyłącz(self):
        import os
        while self.klienci:
            self.klienci[0].rozłącz("SerwerWyłączony")
        os._exit(1)
        exit()
        self.s.close()
        self.s.shutdown()

    def zaloguj(self, dane):
        mycursor = self.mydb.cursor()
        print("Próba zalogowania:", dane)
        if len(dane) < 2:
            return None

        mycursor.execute(f"SELECT id FROM users WHERE\
            login=\"{dane[0]}\" AND password=\"{dane[1]}\";")

        myresult = mycursor.fetchall()

        if myresult:
            print(myresult)
            return myresult[0][0]
        else:
            return None

    def zarejestruj(self, dane):
        mycursor = self.mydb.cursor()

        sql = "INSERT INTO users (login, password) VALUES (%s, %s)"
        val = tuple(dane)
        mycursor.execute(sql, val)

        self.mydb.commit()

        print("1 record inserted, ID:", mycursor.lastrowid)
        return mycursor.lastrowid

    def threaded_client(self, k):
        import traceback
        k.wyślij("Connected")
        reply = ""

        gra = False
        user_id = None
        przeciwnik = None
        numer = None 
        user_nick = None

        while True:
            try:
                data = k.połączenie.recv(2048)
                reply = data.decode("utf-8").lower()

                odpowiedź = "NieznaneZapytanie"

                # Wylogowanie, przypisanie wszytkim zmiennym wartości początkowych
                if reply.startswith("wyloguj"):
                    gra = False
                    user_id = None
                    przeciwnik = None
                    numer = None 
                    user_nick = None
                    k.wyślij("wylogowano")
                    continue
                    
                
                # Obsługa logowania
                if not user_id:
                    dane = reply.split("_")[1:]
                    if reply.startswith("zaloguj"):
                        user_id = self.zaloguj(dane)
                    elif reply.startswith("zarejestruj"):
                        user_id = self.zarejestruj(dane)
                    
                    if user_id:
                        mycursor = self.mydb.cursor()
                        mycursor.execute(f"SELECT login FROM users WHERE id=\"{user_id}\";")
                        myresult = mycursor.fetchall()
                        user_nick = myresult[0][0]
                        odpowiedź = f"zalogowany_{user_id}"
                    else:
                        odpowiedź = "błądlogowania"

                
                elif gra: 

                    # Rezygnacja z gry, np w trakcie oczekiwania na przeciwnika
                    if reply.startswith("zrezygnuj"):
                        self.stoły.pop(numer, None)
                        gra = False
                        odpowiedź = "zrezygnowano"
                    if przeciwnik:
                        przeciwnik.send(str.encode(reply))
                        odpowiedź = None
                    else:
                        if reply.startswith("czekam"):
                            if not self.stoły[numer].czeka:
                                przeciwnik = self.stoły[numer].przeciwnik(k.połączenie)
                                odpowiedź = "1"
                            else:
                                odpowiedź = "0"


                else:
                    if reply.startswith("pobierzstoly"):
                        stoły = [str(i.numer) + ":1" if i.czeka
                            else str(i.numer) + ":0" for i in sorted(self.stoły.values(),
                                key = lambda i: i.numer)]
                        odpowiedź = "stoly_" + "_".join(stoły)

                    # Tworzenie nowego stołu
                    elif reply.startswith("stworzstol"):
                        numer = int(reply.split("_")[1])

                        if numer in self.stoły:
                            odpowiedź = f"stolistnieje"
                        else:
                            self.stoły[numer] = stół.Stół(numer, k.połączenie,user_nick)
                            odpowiedź = f"stol_{numer}:1"
                            odpowiedź = "stolutworzony"
                        gra = True

                    # Dołączanie do istniejącego stołu
                    elif reply.startswith("dolacz"):
                        numer = int(reply.split("_")[1])

                        if numer in self.stoły and self.stoły[numer].czeka:
                            self.stoły[numer].dołącz(k.połączenie)
                            odpowiedź = f"stol_{numer}:0"
                            przeciwnik = self.stoły[numer].przeciwnik(k.połączenie)
                            self.stoły[numer].gracz2_nick = user_nick
                        else:
                            odpowiedź = "stolnieistnieje"
                        gra = True
                #pobieranie nicku przeciwnika 
                if reply.startswith("nickprzeciwnika"):
                    numer = int(reply.split("_")[1])
                    s = self.stoły[numer]
                    if user_nick == s.gracz1_nick:
                        odpowiedź = str(s.gracz2_nick)
                    else:
                        odpowiedź = str(s.gracz1_nick)

                # zmiana pozycji rakietki
                if reply.startswith("ustaw"):
                    print("Y paletki:",reply.split("_")[2])
                    x = float(reply.split("_")[1])
                    y = float(reply.split("_")[2])
                    if self.stoły[numer].gracz1 == k.połączenie:
                        self.stoły[numer].pozycja1 = (x,y)
                        self.stoły[numer].rakieta1.pozycja.x = x
                        self.stoły[numer].rakieta1.pozycja.y = y
                    else: 
                        self.stoły[numer].pozycja2 = (x,y)
                        self.stoły[numer].rakieta2.pozycja.x = x
                        self.stoły[numer].rakieta2.pozycja.y = y
                        
                # zmiana pozycji piłeczki
                if reply.startswith("piłeczka"):
                    szerokość = int(reply.split("_")[1])
                    wysokość = int(reply.split("_")[2])
                    s = self.stoły[numer]
                    s.piłeczka_pozycja_startowa = (szerokość/2, wysokość/2)
                    
                    (x,y) = s.piłeczka_pozycja
                    x += s.prędkość_x
                    y += s.prędkość_y
                    s.piłeczka_pozycja = (x,y)
                    s.piłka.pozycja.x = x
                    s.piłka.pozycja.y = y
                   
                    if s.piłeczka_pozycja[0] < 0 or s.piłeczka_pozycja[0] > szerokość:
                        s.prędkość_x *= -1 

                    if s.piłeczka_pozycja[1] < 0 or s.piłeczka_pozycja[1] > wysokość:
                        s.prędkość_y *= -1

                    # odbijanie od rakietki
                    if s.piłka.pozycja.colliderect(s.rakieta1.pozycja) or s.piłka.pozycja.colliderect(s.rakieta2.pozycja):
                        s.prędkość_y *= -1
                    
                    if s.piłeczka_pozycja[1] < 0:
                        s.score[0] += 1
                        self.reset_piłki(s)
                    elif s.piłeczka_pozycja[1] > wysokość:
                        s.score[1] += 1
                        self.reset_piłki(s)

                    # pomimo, że na serwerze zapisywane są wyniki i pozycja piłki jak dla pierwszego gracza
                    # drugi gracz powinien dostać je symetryczne
                    if s.gracz1 == k.połączenie:
                        odpowiedź = f"zmien.poz.pił_{s.piłeczka_pozycja}_{s.score}_"
                    else:
                        (x_pił,y_pił) = s.piłeczka_pozycja
                        zwracana_pozycja = (szerokość - x_pił, wysokość - y_pił)
                        zwracany_score = s.score[::-1]
                        odpowiedź = f"zmien.poz.pił_{zwracana_pozycja}_{zwracany_score}_"


                if reply == "__shut_down__":
                    print("SHUT DOWN")
                    self.wyłącz()

                if odpowiedź:
                    k.wyślij(odpowiedź)

                if not data:
                    print("Disconnected")
                    break
                else:
                    print("From:",user_id)
                    print("Received: ", reply)
                    print("Sending : ", odpowiedź)
                    print("")

            except Exception:
                traceback.print_exc()
                break


        # Usunięcie gier, w których brał udział użytkownik.
        # Przy zerwaniu połączenia usuwa pozostawione gry.
        ### Uwaga, jeśli jeden gracz wyjdzie może powodować problemy po stronie 2 gracza
        ### (odwoływanie się do usuniętego elementu słownika)
        if k:
            for stol in self.stoły:
                if (self.stoły[stol].gracz1 == k.połączenie
                    or self.stoły[stol].gracz1 == k.połączenie):
                   self.stoły.pop(stol, None)

        print("Lost connection")
        k.rozłącz()
    
    def reset_piłki(self,stół):
        stół.piłeczka_pozycja = stół.piłeczka_pozycja_startowa

    def słuchaj(self):
        self.s.listen()
        print("Waiting for a connection, Server Started")

        while True:
            try:
                conn, addr = self.s.accept()
                k = klient.Klient(conn, self) 
                print("Connected to:", addr)
                self.klienci.append(k)

                start_new_thread(Serwer.threaded_client, (self, k,))
            except OSError:
                pass


if __name__ == "__main__":
    ip = "localhost"
    port = 5555

    serwer = Serwer(ip, port)
    serwer.słuchaj()
