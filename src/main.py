__author__ = 'Petr'

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class Ad:
    tp = "prodam"

    def __init__(self):
        pass


def download_page_content(url):
    try:
        r = requests.get(url)
        return r.text
    except:
        # Proper exception handling
        print("Error getting the request")
        return None


def analyze_one_ad(ad_html):
    print("==================================================================")

    # HEADER INFO
    divh = ad_html.find("div", {"class": "list-ads-header"})
    info = divh.text.split('|')
    time = info[3][10:]
    try:
        time = datetime.strptime(time, '%d.%m.%Y, %H:%M ')
    except:
        print("Failed converting the datetime")
        return

    print(time)
    print("Type: {}, section: {}, brand: {}".format(info[0], info[1], info[2]))
    try:
        adid = re.search('.*=(\d+)', divh.a['href']).group(1)
        print("AdId: {}".format(adid))
    except AttributeError:
        print("Regex fail while parsing add")
        return

    # FOOTER INFO
    divf = ad_html.find("div", {"class": "list-ads-footer"})
    print(divf.a.text)
    print(divf.a['title']) ## CHECK WHAT THIS REALLY IS

    uid = divf.findAll('a')[1::2]
    try:
        uid = re.search('.*=(\d+)', uid[0]['href']).group(1)
    except AttributeError:
        print("Regex fail while parsing add")
        return

    print("UserID: {}".format(uid))
    print("\n\n")
    # Telnumber:
    print(divf.findAll('a')[1::2][0].next_sibling)
    print("\n\n")

    # BODY INFO
    divc = ad_html.find("div", {"class": "list-ads-row-content"})
    ad_name = divc.find("p", {"class": "list-ads-name"})
    print("AdName: {}".format(ad_name.text))
    ad_content = divc.findAll('p')[1::2][0].text
    print("AdContent: {}".format(ad_content))
    ## If we detect that there is word "cely text inzeratu" we need to grab the ad from seprate page
    try:
        price = divc.findAll('p')[2::3][0].strong.text
        print(price)
    except:
        print("No price found")






def find_ads_on_page(url):
    page_content = download_page_content(url)

    if not page_content:
        return None

    soup = BeautifulSoup(page_content, 'html.parser')
    ads = soup.findAll("div", {"class": "list-ads-row"})
    print("On page: {}, found: {} ads".format(url, len(ads)))
    for x in ads:
        analyze_one_ad(x)




if __name__ == "__main__":
    find_ads_on_page("http://www.paladix.cz/bazar/index.php?from=0")
    #find_ads_on_page("http://www.paladix.cz/bazar/index.php?from=10")
    #find_ads_on_page("http://www.paladix.cz/bazar/index.php?from=400")
