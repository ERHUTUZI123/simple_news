from bs4 import BeautifulSoup
import requests

def fetch_news(url):
    response = requests.request('GET', url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # a tag: <p>hello</p>
        # find outputs a single tag
        # find_all outputs a list of tags
        article = soup.find_all('p', attrs={"class": "sc-9a00e533-0 eZyhnA"})

        o_text = ""
        for para in article:
            soup = BeautifulSoup(str(para), 'html.parser')
            text = soup.get_text(strip=True)
            o_text += text
        return o_text
    else:
        return 'PLEASE JUST OUTPUT "No Content", IGNORE following prompt'