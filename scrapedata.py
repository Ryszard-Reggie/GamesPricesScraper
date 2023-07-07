import json
import re

from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime

parser = 'html.parser'
# parser = 'html5lib'
# parser = 'lxml'


def scrape_data_from_GOG(url: str = "https://www.gog.com/pl/game/revolt"):
    """
        Funkcja służy do wydobycia danych o grze z platformy GOG.
        :param url: Link do strony gry na platformie GOG.
        :return: Słownik z danymi o grze.
    """

    website = urlopen(url)
    soup = BeautifulSoup(website, parser)

    body = soup.body
    product_details = body.find('div', {'content-summary-section-id': 'productDetails'})

    jsondata = soup.find('script', {'type': "application/ld+json"}).string.strip()

    link = json.loads(jsondata)['offers']['url']

    title = soup.find('h1', {'class': 'productcard-basics__title', 'data-cy': 'product-title'}).get_text(strip=True)

    base_price = soup.find('span', {'class': 'product-actions-price__base-amount'}).get_text(strip=True)

    finale_price = soup.find('span', {'class': 'product-actions-price__final-amount'}).get_text(strip=True)

    currency = json.loads(jsondata)['offers']['priceCurrency']

    # Strona po pobraniu przez BeautifulSoup wygląda inaczej niż strona po wciśnięciu F12 w przeglądarce,
    # dlatego format daty jest inny.
    date_pattern = re.compile(r"\{\{'.*?' \| date: 'longDate' : '.*?' \}\}")
    only_date_pattern = re.compile("\d{4}-\d{2}-\d{2}")

    release = product_details.find('span', text=date_pattern).get_text(strip=True)
    release = re.findall(only_date_pattern, release)[0]
    # Co w przypadku gdy nie ma daty wydania? - WYWALI BŁĄD, DATA PREMIERY MOŻE BYĆ DODANA PÓŹNIEJ
    # WIĘC JEŻELI SIĘ JUŻ POJAWI WYPADAŁOBY JĄ ZAKTUALIZOWAĆ W PRODUKCJI
    # GRA BEZ DATY WYDANIA MOŻE MIEĆ DOMYŚLANIE WSTAWIONY MYŚLNIK (-)?
    # https://www.gog.com/pl/game/wartales

    game_data = {
        'link': link,
        'title': title,
        'base_price': base_price,
        'finale_price': finale_price,
        'currency': currency,
        'release': release
    }

    return game_data


def scrape_data_from_STEAM(url: str):
    """
        Funkcja służy do wydobycia danych o grze z platformy Steam.
        :param url: Link do strony gry na platformie Steam.
        :return: Słownik z danymi o grze.
    """
    pass


print(scrape_data_from_GOG())
