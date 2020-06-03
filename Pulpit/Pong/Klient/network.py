import socket
from _thread import *
import sys
import traceback


class Network:
    """ Klasa odpowiadająca za połączenie klienta z serwerem """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.czekaj = True
        self.addr = (self.server, self.port)
        odp = self.połącz()
        if odp:
            self.połączony = True
        else:
            self.połączony = False


    def obsłuż(self, odpowiedź):
        print("\nOdpowiedź: " + odpowiedź)
        if odpowiedź == "SerwerWyłączony":
            pass

    def obsługa_komunikatów(self, funkcja, inne):
        reply = ""


        while not self.czekaj:
            try:
                data = self.client.recv(2048)
                reply = data.decode("utf-8").lower()

                funkcja(reply, inne)

                if not data:
                    print("Disconnected")
                    break

            except Exception:
                traceback.print_exc()
                break

        print("Lost connection", self.czekaj)
        self.połączony = False


    def połącz(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def wyślij(self, data):
        try:
            self.client.send(str.encode(data))
            if self.czekaj:
                return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)

    def słuchaj(self, funkcja = None, inne = None):
        self.czekaj = False
        try:
            start_new_thread(Network.obsługa_komunikatów, (self, funkcja, inne))
        except OSError:
            traceback.print_exc()

    def zakoncz_nasluchiwanie(self):
        self.czekaj = True
