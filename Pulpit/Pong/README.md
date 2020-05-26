# Pong
W ramach projektu planujemy wykonać grę w Ponga przez Internet. Aplikacja kliencka będzie łączyć się z serwerem, pełniącym rolę pośrednika w grze. System umożliwi prowadzenie wielu rozgrywek jednocześnie przez zastosowanie systemu „stołów”. Użytkownik będzie mógł utworzyć nowy stół lub dołączyć do istniejącej już gry z wolnym miejscem. Każdy użytkownik będzie miał utworzone konto, z którym będą związane na przykład statystyki danego gracza czy historia przeprowadzonych gier. Dane każdego konta przechowywanebędą w bazie danych SQL. Ponad to, możliwe będzie sprawdzenie swojej aktualnej pozycji w rankingu. 

Użyte biblioteki:
pygame
PyQt5
mysql-connector-python

Konfiguracja MySQL:
host="localhost",
user="server",
passwd="zaq1@WSX",
database="pong"

Kod SQL:
CREATE TABLE users (
id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
login VARCHAR(30) NOT NULL,
password VARCHAR(30) NOT NULL
);

