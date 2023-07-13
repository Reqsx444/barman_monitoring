import os
import sys
import datetime
import shutil
import subprocess
from airium import Airium

# Pobieramy dzisiejszą datę bez godziny i modyfikujemy jej format z YY-MM-DD na YYMMDD
now = datetime.datetime.now().date()
nowformat = now.strftime("%Y%m%d")
directory = "/storage/barman-backup/"
archive = "/var/barman_archive/"


def hashline():
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('<span style="font-size: 1.3em">')
        f.write('#################################################</br>')
        f.write('</span>')


# Tworzymy, otwieramy i dodajemy datę do pliku raportowego, a następnie zamykamy go
with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<body style="background-color: #d7d9db; text-alignt: center" style="padding: 2%" style="margin: 0">')
    f.write('<h1>RAPORT BARMAN DATASPACE WARSZAWA</h1>')
    f.write(f'<h2>DATA: {now} </h2>')

# Pobieramy dostępne konfiguracje backupów Barman i usuwamy z listy template'y
configs = os.listdir("/etc/barman.d/")
configs.remove('streaming-server.conf-template')
configs.remove('ssh-server.conf-template')
configs.remove('passive-server.conf-template')
configs.sort(reverse=True)

hashline()

# Tworzymy nową listę na bazie konfiguracji i usuwamy ostatnie 5 znaków z każdej pozycji (.conf)
backups = [i[:-5] for i in configs]
backups.sort(reverse=True)

# Sprawdzamy stan każdego konfigu i wypisujemy go
with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h3>Konfiguracje dostępne na serwerze:</h3>')

repair = 0
successbck = []
failedbck = []

for i in backups:
    serverstate = os.system(f'barman check {i} >/dev/null 2>&1')
    if serverstate == 0:
        successbck.append(i)
    else:
        failedbck.append(i)

successbck.sort(reverse=True)
failedbck.sort(reverse=True)

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h4>Poprawny:</h4>')

# Próba naprawienia konfigu w stanie FAILED
for x in failedbck:
    os.system(f'rm -rf {directory}{x}/errors/* > /dev/null 2>&1')
    os.system(f'barman receive-wal {x} --stop > /dev/null 2>&1')
    os.system(f'barman receive-wal {x} --reset > /dev/null 2>&1')
    os.system(f'barman switch-xlog --force --archive {x} > /dev/null 2>&1')
    repair = 1

# Formatowanie zmiennych dla HTML
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
    f.write('<p style="color: #248f24">')
    f.write(successbck + '</br>')
    f.write('</p>')

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<h4>Błędny:</h4>')

with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('<p style="color: #b30000">')
    f.write(failedbck + '</br>')
    f.write('</p>')

if repair == 1:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('<p style="font-weight: bold">')
        f.write('!Podjęto próbę automatycznej naprawy konfiguracji! </br>')
        f.write('</p>')

hashline()
runclear = int(0)
toclear = []

for i in backups:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('<span style="font-weight: bold">')
        f.write('</br>' f'Stan wykonanych dziś kopii dla {i}:' '</br>')
        f.write('</span>')

    exist = None
    for file in sorted(os.listdir(directory + i + "/base")):
        if file.startswith(nowformat):
            backupstate = os.system(f'barman check-backup {i} {file} >/dev/null 2>&1')
            exist = i
            if backupstate == 0:
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('<span style="color: #248f24">')

                os.system(f'echo "{file} jest poprawny </br>" >> raport{nowformat}.txt')
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('</span>')
            else:
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('<span style="color: #b30000">')

                os.system(f'echo "{file} jest uszkodzony </br>" >> raport{nowformat}.txt')
                with open(f'raport{nowformat}.txt', 'a') as f:
                    f.write('</span>')
                toclear.append(i)
                runclear = int(1)
    if exist is None:
        with open(f'raport{nowformat}.txt', 'a') as f:
            f.write('<span style="color: #b54a55">')
            f.write(f'BRAK KOPII' '</br>')
            f.write('</span>')

# Uruchomienie skryptu do czyszczenia w przypadku wykrycia uszkodzonych kopii
with open(f'raport{nowformat}.txt', 'a') as f:
    f.write('</br>')

hashline()

if runclear == 1:
    for x in toclear:
        os.system(f'./barman_clear.sh -n {x}')
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('<p style="color: #e65c00" style="font-weight: bold">Czyszczenie uszkodzonych kopii zakończone</p>' '</br>')
else:
    with open(f'raport{nowformat}.txt', 'a') as f:
        f.write('<p style="color: #248f24" style="font-weight: bold"> Brak uszkodzonych kopii - czyszczenie pominięte</p>' '</br>')

a = Airium()
converthtml = os.popen(f'cat raport{nowformat}.txt').read()
# Generating HTML file
a('<!DOCTYPE html>')
with a.html(lang="pl"):
    with a.head():
        a.meta(charset="utf-8")
        a.title(_t="Automatyczny Raport Barman 3S")
    with a.div():
        a.img(src='https://wiki.dataspace.pl/wp-content/themes/starter-theme-master/img/data-space-logo.png',
              alt='DataSpace Logo')
    with a.body():
        with a.h3(id="id23345225", kclass='main_header'):
            a(f'{converthtml}')
# Casting the file to a string to extract the value
html = str(a)
# Casting the file to UTF-8 encoded bytes:
html_bytes = bytes(a)

with open(f'raport{nowformat}.html', 'wb') as f:
    f.write(bytes(html, encoding='utf8'))

# Przesłanie raportu mailem
os.system(
    f'echo "W załączniku raport za dzień {now}" | mail -s "Automatyczny Raport Barman" damian.golal@dataspace.pl -A raport{nowformat}.html')
shutil.move(f'raport{nowformat}.html', archive)
os.remove(f'raport{nowformat}.txt')
