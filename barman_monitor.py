#Importujemy potrzebne moduły
import os, sys, datetime
from airium import Airium

#Pobieramy dzisiejszą datę bez godziny i modyfikujemy jej format z YY-MM-DD na YYMMDD
now = datetime.datetime.now().date()
nowformat = now.strftime("%Y%m%d")
directory = "/storage/barman-backup/"

#html_content = f"<html> <head> </head> <body> </body> </html>"
#with open(f'raport{nowformat}.html', 'w') as f:
#    f.write(html_content)
#f.close()

#Tworzymy, otwieramy i dodajemy datę do plik raportowego, a następnie zamykamy go
with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h1>RAPORT BARMAN 3S WARSZAWA</h1>')
    f.write(f'<h2>DATA: {now} </h2>')
f.close()

#Pobieramy dostępne konfiguracje backupów Barman i usuwamy z listy template'y
configs = os.listdir("/etc/barman.d/")
configs.remove('streaming-server.conf-template')
configs.remove('ssh-server.conf-template')
configs.remove('passive-server.conf-template')

#Wypisujemy dostępne konfiguracje
with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('</br>' '########################################')
    f.write('</br>' '</br>' 'Konfiguracje dostępne na serwerze:' '</br>')
f.close()

for i in configs:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write(f'{i}' '</br>')
f.close()
with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br>' '########################################' '</br>')
f.close()

#Tworzymy nową listę na bazie konfiguracji i usuwamy ostatnie 5 znaków z każdej pozycji (.conf)
backups = [i[:-5] for i in configs]

#Sprawdzamy stan każdego konfigu i wypisujemy go
with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h3>Stan konfiguracji:</h3>')
f.close()

successbck = []
failedbck = []

for i in backups:
    serverstate = os.system(f'barman check {i} >/dev/null 2>&1')
    if serverstate == 0:
        successbck.append(i)
    else:
        failedbck.append(i)

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h4>Poprawny:</h4>')
f.close()

#Formatowanie zmiennych dla HTML
successbck = str(successbck)
failedbck = str(failedbck)
successbck = successbck.replace(',', '</br>')
failedbck = failedbck.replace(',', '</br>')
successbck = successbck.replace('[', '')
failedbck = failedbck.replace('[', '')
successbck = successbck.replace(']', '')
failedbck = failedbck.replace(']', '')
successbck = successbck.replace("'", '')
failedbck = failedbck.replace("'", '')

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<p style="color: green">')
    f.write(successbck+'</br>')
    f.write('</p>')
    f.close()

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h4>Błędny:</h4>')
f.close()

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<p style="color: red">')
    f.write(failedbck+'</br>')
    f.write('</p>')
f.close()

#Wypisujemy wykonane dziś kopie dla każdej konfiguracji
with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('########################################' '</br>')
f.close()

for i in backups:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br>' f'Wykonane dziś kopie dla konfiguracji {i}:' '</br>')
    f.close()
    test = None
    for file in os.listdir(directory+i+"/base"):
        if file.startswith(nowformat):
            with open(f'raport{nowformat}.txt', 'a') as f:
                f.write(f'{file}' '</br>')
            f.close()
            test = i
    if test == None:
        with open(f'raport{nowformat}.txt', 'a') as f:
            f.write('<span style="color: red">')
            f.write(f'BRAK KOPII' '</br>')
            f.write('</span>')
        f.close()

#Sprawdzamy wykonane dziś kopie i wypisujemy stan każdej z nich
with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br>' '########################################' '</br>')
f.close()

runclear = int(0)
for i in backups:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br>' f'Stan wykonanych dziś kopii dla {i}:' '</br>')
    f.close()

    for file in os.listdir(directory+i+"/base"):
        if file.startswith(nowformat):
            backupstate = os.system(f'barman check-backup {i} {file} >/dev/null 2>&1')
            if backupstate == 0:
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('<span style="color: green">')
                f.close()
                os.system(f'echo "{file} jest poprawny </br>" >> raport{nowformat}.txt')
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('</span>')
                f.close()
            else:
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('<span style="color: red">')
                f.close()
                os.system(f'echo "{file} jest uszkodzony </br>" >> raport{nowformat}.txt')
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('</span>')
                f.close()
                runclear = int(1)

#Uruchomienie skryptu do czyszczenia w przypadku wykrycia uszkodzonych kopii
with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br>' '########################################' '</br>')
f.close()

if runclear == 1:
    os.system( "./barman_clear.sh")
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br><p style="color: yellow">Czyszczenie uszkodzonych kopii zakończone</p>' '</br>')
    f.close()

else:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('</br><p style="color: green"> Brak uszkodzonych kopii - czyszczenie pominięte</p>' '</br>')
    f.close()

a = Airium()
converthtml = os.popen(f'cat raport{nowformat}.txt').read()
# Generating HTML file
a('<!DOCTYPE html>')
with a.html(lang="pl"):
    with a.head():
        a.meta(charset="utf-8")
        a.title(_t="Automatyczny Raport Barman 3S")
    with a.div():
        a.img(src='https://wiki.dataspace.pl/wp-content/themes/starter-theme-master/img/data-space-logo.png', alt='DataSpace Logo')
    with a.body():
        with a.h3(id="id23345225", kclass='main_header'):
            a(f'{converthtml}')
# Casting the file to a string to extract the value
html = str(a)
# Casting the file to UTF-8 encoded bytes:
html_bytes = bytes(a)

with open(f'raport{nowformat}.html', 'wb') as f:
    f.write(bytes(html, encoding='utf8'))

#Przesłanie raportu mailem
os.system(f'echo "W załączniku raport za dzień {now}" | mail -s "Automatyczny Raport Barman" mail@test.pl -A raport{nowformat}.html')
os.remove(f'raport{nowformat}.html')
os.remove(f'raport{nowformat}.txt')
