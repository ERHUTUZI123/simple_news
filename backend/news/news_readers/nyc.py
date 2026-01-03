from bs4 import BeautifulSoup
import requests

def fetch_news(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # a tag: <p>hello</p>
        # find outputs a single tag
        # find_all outputs a list of tags
        article = soup.find_all('p', attrs={"class": "css-ac37hb evys1bk0"})
        o_text = ""
        for para in article:
            soup = BeautifulSoup(str(para), 'html.parser')
            text = soup.get_text(strip=True)
            o_text += text
        return o_text
    else:
        return response.status_code