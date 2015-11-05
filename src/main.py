import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json
__author__ = 'Petr'


def download_page_content(url):
    try:
        r = requests.get(url)
        text = bytes(r.text,  encoding='iso-8859-1')
        return text
    except Exception as e:
        print(e)
        # Proper exception handling
        print("Error getting the request")
        return None


def analyze_one_ad(ad_html,verbose = False):
    if verbose:
        print("==================================================================")
    ad_json = {}

    # HEADER INFO
    divh = ad_html.find("div", {"class": "list-ads-header"})
    info = divh.text.split('|')
    time = info[3][10:]
    ad_json['time'] = None
    try:
        time = datetime.strptime(time, '%d.%m.%Y, %H:%M ')
        ad_json['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(e)
        print("Failed converting the datetime")
        return

    ad_json['type'] = None
    ad_json['type'] = info[0]
    ad_json['section'] = None
    ad_json['section'] = info[1]
    ad_json['brand'] = info[2]

    if verbose:
        print("Type: {}, section: {}, brand: {}".format(info[0], info[1], info[2]))

    ad_json['ad_id'] = None

    try:
        adid = re.search('.*=(\d+)', divh.a['href']).group(1)
        ad_json['ad_id'] = adid
        if verbose:
            print("AdId: {}".format(adid))
    except AttributeError:
        if verbose:
            print("Regex fail while parsing add")
        return

    # FOOTER INFO
    divf = ad_html.find("div", {"class": "list-ads-footer"})

    ad_json['email'] = divf.a.text

    if verbose:
        print(divf.a.text)
        print(divf.a['title']) ## CHECK WHAT THIS REALLY IS

    ad_json['user_name'] = divf.a['title']
    ad_json['user_id'] = None

    uid = divf.findAll('a')[1::2]
    try:
        uid = re.search('.*=(\d+)', uid[0]['href']).group(1)
        ad_json['user_id'] = uid
    except AttributeError:
        print("Regex fail while parsing add")
        return

    if verbose:
        print("UserID: {}".format(uid))

    ad_json['tel'] = None
    # Telnumber:
    tel_help = divf.findAll('a')[1::2][0].next_sibling
    tel = ""
    for x in tel_help:
        if x.isdigit():
            tel += x
    if verbose:
        print("Tel number: {}".format(tel))

    if len(tel) != 0:
        ad_json['tel'] = tel
    ## WHAT TO DO IF TEL IS EMPTY

    # BODY INFO
    divc = ad_html.find("div", {"class": "list-ads-row-content"})
    ad_name = divc.find("p", {"class": "list-ads-name"})
    ad_json['ad_name'] = ad_name.text
    if verbose:
        print("AdName: {}".format(ad_name.text))
    ad_content = divc.findAll('p')[1::2][0].text

    # TODO ADCONTENT
    ad_json['content'] = ad_content
    if verbose:
        print("AdContent: {}".format(ad_content))
    ## If we detect that there is word "cely text inzeratu" we need to grab the ad from seprate page

    ad_json['price'] = None
    try:
        price = divc.findAll('p')[2::3][0].strong.text

        pr = ""
        for x in price:
            if x.isdigit():
                pr += x
        if verbose:
            print("Price: {}".format(pr))
        ad_json['price'] = pr
    except Exception as e:
        if verbose:
            print(e)
            print("No price found")

    # Detect Image
    ad_json['img'] = None
    img = divc.findAll("img")
    if len(img) != 0:
        ad_json['img'] = img[0]['src']
        if verbose:
            print("Image found: {}".format(img[0]['src']))
            print("Image len: {}".format(len(img)))
    else:
        if verbose:
            print("NO image found")

    ad_json['location'] = None
    ad_json['link'] = None
    lok = divc.findAll("p")
    for x in lok:
        # Detect lokalita
        if "lokalita: " in x.text:
            ad_json['location'] = x.text[22:]
            if verbose:
                print("\nLOKAILTA {}\n".format(x.text[22:]))
        # Detect link
        if "Link:" in x.text:
            if not (x.a is None):
                ad_json['link'] = x.a['href']
                if verbose:
                    print("\nLink:|{}|".format(x.a['href']))

    if verbose:
        print(json.dumps(ad_json, ensure_ascii=False))
    return ad_json


def find_ads_on_page(url):
    page_content = download_page_content(url)

    if not page_content:
        return None

    soup = BeautifulSoup(page_content, 'html.parser')
    ads = soup.findAll("div", {"class": "list-ads-row"})
    print("On page: {}, found: {} ads".format(url, len(ads)))
    jsons = []

    for x in ads:
        jsons.append(analyze_one_ad(x, False))
    return jsons




if __name__ == "__main__":
    jsons = []
    for x in range(2000, 5000, 10):
        jsons.append(find_ads_on_page("http://www.paladix.cz/bazar/index.php?from="+str(x)))

    final_json = []
    for x in jsons:
        for y in x:
            final_json.append(y)

    db = {'db': {'table1': final_json}}

    import codecs
    with codecs.open('data.json', 'w', 'utf-8') as outfile:
        outfile.write(json.dumps(db, ensure_ascii=False))
