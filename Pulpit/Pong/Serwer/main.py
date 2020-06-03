import server


def main():
    """ Uruchamia serwer """
    ip = "localhost"
    port = 5555

    serwer = server.Serwer(ip, port)
    serwer.słuchaj()


if __name__ == "__main__":
    main()
