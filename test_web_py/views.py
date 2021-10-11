from django.shortcuts import render
from .models import Projet

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Create your views here.

def hello(request):
    main()
    print('Successfully')
    projet = Projet.objects.all()
    return render(request, 'index.html')

def main():
    writer = pd.ExcelWriter('Liquideo.xlsx', engine='xlsxwriter')
    writer.save()

    baseurl = 'https://www.liquideo.com/'
    productlinks = []
    boardlist = []
    headers = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/92.0.4515.107 Safari/537.36 '
        # 'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
        # 'like Gecko) Mobile/15E148'
    }

    urls = all_links()
    for url in urls:
        marque = find_marque(url)
        productlinks = []
        productlinks = scrap_page(productlinks, url)
        scrap_product(productlinks, boardlist, headers, marque)

    df = pd.DataFrame(boardlist)
    print(df.head(50))

    writer = pd.ExcelWriter('Liquideo.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()

    send_mail()


def all_links():
    urls = ['https://www.liquideo.com/fr/74-e-liquides-evolution']
    return urls


def find_marque(url):
    marque = ''

    if url == 'https://www.liquideo.com/fr/74-e-liquides-evolution':
        marque = 'Liquideo Evolution'
    elif url == 'https://www.liquideo.com/fr/172-monsieur-bulle':
        marque = 'Monsieur Bulle'
    elif url == 'https://www.liquideo.com/fr/131-e-liquides-juice-heroes':
        marque = 'Juice Heroes'
    elif url == 'https://www.liquideo.com/fr/163-e-liquides-freeze':
        marque = 'Freeze'
    elif url == 'https://www.liquideo.com/fr/162-e-liquides-fifty-salt':
        marque = 'Fifty Salt'
    elif url == 'https://www.liquideo.com/fr/152-e-liquides-tentation':
        marque = 'Tentation'
    elif url == 'https://www.liquideo.com/fr/80-e-liquides-dandy':
        marque = 'Dandy'
    elif url == 'https://www.liquideo.com/fr/138-e-liquides-xbud':
        marque = 'Xbud'
    elif url == 'https://www.liquideo.com/fr/154-e-liquides-fantasia':
        marque = 'Fantasia'
    elif url == 'https://www.liquideo.com/fr/89-e-liquides-muertes':
        marque = 'Muertes'
    elif url == 'https://www.liquideo.com/fr/130-e-liquides-liquideo-sodas':
        marque = 'Sodas'
    elif url == 'https://www.liquideo.com/fr/159-e-liquides-standard':
        marque = 'Standard'
    elif url == 'https://www.liquideo.com/fr/174-diy-liquideo-factory':
        marque = 'DIY Liquideo Factory'
    elif url == 'https://www.liquideo.com/fr/176-multi-freeze':
        marque = 'Multi Freeze'
    return marque


def scrap_page(productlinks, url):

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    productlist = soup.find_all('li', class_='ajax_block_product')
    for item in productlist:
        i = 0
        for link in item.find_all('a', href=True):
            if i == 1:
                break
            productlinks.append(link['href'])
            i = 1
    return productlinks


def scrap_product(productlinks, boardlist, headers, marque):
    for link in productlinks:
        print(link)
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        soup2 = BeautifulSoup(r.text, 'html.parser')
        name = scrap_title(soup)
        price = scrap_price(soup)
        description = scrap_description(soup)
        long_desc = scrap_long_description(soup)
        saveur, pgbg, tdn, conditionnement, contenance, bouchon, securite = scrap_caracteristique(soup)
        img = scrap_img(soup2)
        board = {
            '01: Nom du produit': name,
            '02: Prix': price,
            '03: Description': description,
            '04: Description longue': long_desc,
            '05: Saveur': saveur,
            '06: PG/VG': pgbg,
            '07: Taux de nicotine': tdn,
            '08: Conditionnement': conditionnement,
            '09: Contenance': contenance,
            '10: Bouchon': bouchon,
            '11: Securite': securite,
            '12: Marque': marque,
            '13: Image': img,
        }
        boardlist.append(board)
        print('Saving: ', board['01: Nom du produit'])


#a mettre dans un autre .py et le lier a celui ci
def scrap_title(soup):
    try:
        name = soup.find('h1', itemprop='name').text.strip()
    except:
        name = 'no name'
    return name


def scrap_price(soup):
    try:
        price = soup.find(id="our_price_display").text.strip()
    except:
        price = 'no price'
    return price


def scrap_description(soup):
    try:
        description = soup.find('div', itemprop='description').text.strip()
    except:
        description = 'no description'
    return description


def scrap_long_description(soup):
    try:
        long_desc = soup.find('div', class_='more-info-desc').text.strip()
    except:
        long_desc = 'no long description'
    print(long_desc)
    return long_desc


def scrap_caracteristique(soup):
    saveur = ''
    pgbg = ''
    tdn = ''
    conditionnement = ''
    contenance = ''
    bouchon = ''
    securite = ''
    try:
        caracteristique = soup.find('section', class_='page-product-box').text.strip()
    except:
        caracteristique = 'no caracteristique'

    saveur = scrap_saveur(caracteristique, saveur)
    pgbg = scrap_pgbg(caracteristique, pgbg)
    tdn = scrap_tdn(caracteristique, tdn)
    conditionnement = scrap_conditionnement(caracteristique, conditionnement)
    contenance = scrap_contenance(caracteristique, contenance)
    bouchon = scrap_bouchon(caracteristique, bouchon)
    securite = scrap_securite(caracteristique, securite)
    return saveur, pgbg, tdn, conditionnement, contenance, bouchon, securite


def scrap_saveur(caracteristique, saveur):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'S' and caracteristique[i + 1] == 'a'):
            i += 7
            while (caracteristique[i] != 'P'):
                saveur = saveur + caracteristique[i]
                i += 1
            break
    if (saveur == 'Tabac\n\n\n'):
        saveur = 'Classique'
    elif (saveur == 'Tabac, Fresh\n\n\n'):
        saveur = 'Classique, Fresh'
    elif (saveur == 'Gourmand, Tabac\n\n\n'):
        saveur = 'Gourmand, Classique'
    elif (saveur == 'Tabac, Gourmand\n\n\n'):
        saveur = 'Classique, Gourmand'
    return saveur


def scrap_pgbg(caracteristique, pgbg):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'P' and caracteristique[i + 1] == 'G'):
            i += 6
            while (caracteristique[i] != 'T'):
                if (caracteristique[i] == 'D'):
                    break
                pgbg = pgbg + caracteristique[i]
                i += 1
            break
    return pgbg


def scrap_tdn(caracteristique, tdn):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'T' and caracteristique[i + 2] == 'u'):
            i += 17
            while (caracteristique[i] != 'C'):
                tdn = tdn + caracteristique[i]
                i += 1
            break
    return tdn


def scrap_conditionnement(caracteristique, conditionnement):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'C' and caracteristique[i + 3] == 'd'):
            i += 16
            while (caracteristique[i] != 'C'):
                if (caracteristique[i] == 'S' or caracteristique[i] == 'B'):
                    break
                conditionnement = conditionnement + caracteristique[i]
                i += 1
            break
    return conditionnement


def scrap_contenance(caracteristique, contenance):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'C' and caracteristique[i + 3] == 't'):
            i += 11
            while (caracteristique[i] != 'B'):
                contenance = contenance + caracteristique[i]
                i += 1
            break
    return contenance


def scrap_bouchon(caracteristique, bouchon):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'B' and caracteristique[i + 2] == 'u'):
            i += 8
            while (caracteristique[i] != 'E'):
                if (caracteristique[i] == 'D' or caracteristique[i + 1] == 'S'):
                    break
                bouchon = bouchon + caracteristique[i]
                i += 1
            break
    return bouchon


def scrap_securite(caracteristique, securite):
    for i in range(len(caracteristique)):
        if (caracteristique[i] == 'S' and caracteristique[i + 2] == 'c' and caracteristique[i + 9] != 'e'):
            i += 9
            while (caracteristique[i] != 'D'):
                securite = securite + caracteristique[i]
                i += 1
            break
    return securite


def scrap_img(soup2):
    dest = ''
    j = 0
    try:
        all_images = soup2.find_all('img', itemprop='image')
        img = str(all_images[0])
        for i in range(len(img)):
            if (img[i] == 's' and img[i + 1] == 'r' and img[i + 2] == 'c'):
                i += 5
                while (img[i] != '"'):
                    dest = dest + img[i]
                    i += 1
                break
    except(AttributeError):
        dest = 'no img'
    return dest


def send_mail():
    smtp_server = 'smtp.gmail.com'
    port = 587
    destinateur = 'BOT.tendance.locale@gmail.com'
    password = 'BotScrapping01&'
    destinataire = 'nael@tendancelocale.fr'
    message = MIMEMultipart('alternative')
    subject = 'envoie d\'un fichier'
    message['From'] = destinateur
    message['To'] = destinataire
    istls = True

    msg = MIMEMultipart()
    msg['From'] = destinateur
    msg['To'] = destinataire
    msg['Subject'] = subject
    message.attach(MIMEText('envoyer une pièce jointe', 'plain'))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("Liquideo.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Liquideo.xlsx"')
    msg.attach(part)

    # context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
    # SSL connection only working on Python 3+
    smtp = smtplib.SMTP(smtp_server, port)
    print("Successfully")
    if istls:
        smtp.starttls()
    smtp.login(destinateur, password)
    smtp.sendmail(destinateur, destinataire, msg.as_string())
    smtp.quit()