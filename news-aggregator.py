import json
import subprocess
import validators
import time
import csv

from urllib import parse
from lxml import html
from pyvirtualdisplay import Display
from selenium import webdriver
from bs4 import BeautifulSoup

CONFIG_FILE = 'config.json'
NEWS_FILE = 'news.csv'
HTML_FILE = 'news.html'


def get_page_phantomjs(url):
    bashCommand = 'phantomjs fetchPage.js ' + url
    print(bashCommand)

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)  # , cwd='path\to\somewhere')
    output, error = process.communicate()
    # print('out', output)
    # print('err', error)
    return output


def get_page_firefox(url):
    display = Display(visible=0, size=(800, 600))
    display.start()

    browser = webdriver.Firefox()
    browser.get(url)
    time.sleep(5)

    output = browser.page_source
    browser.quit()
    display.stop()
    return output


def save_page_source(source):
    fileName = '/tmp/' + (newsSource['Name'] + '.html').lower()
    file = open(fileName, "w")
    file.write(source)
    file.close()


def get_config(config_file):
    with open(config_file) as data_file:
        data = json.load(data_file)
        return data

def get_old_news(file):
    output = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            output.append({'TimeStamp': row[0], 'Date': row[1], 'Title': row[2]})
    return output



config = get_config(CONFIG_FILE)
news_sources = config['newsSources']

old_news = get_old_news(NEWS_FILE)

scraped_data = []

for news_source in news_sources:
    if news_source['Fetch'] == "true":

        # print(news_source['Name'])

        # output = get_page_phantomjs(newsSource['Url'])
        output = get_page_firefox(news_source['Url'])

        # save_page_source(output)

        newsItems = html.fromstring(output).xpath(news_source['PreExtractionRules'])

        for newsItem in newsItems:
            date = newsItem.xpath(news_source['ExtractionRules']['Date'])[0].text
            print(date)
            title = newsItem.xpath(news_source['ExtractionRules']['Title'])[0].text
            print(title)
            href = newsItem.xpath(news_source['ExtractionRules']['Address'])[0].attrib['href']
            if (validators.url(href)):
                url = href
            else:
                page = parse.urlparse(news_source['Url'])
                if not (href.startswith('/')):
                    href = '/' + href
                url = page.scheme + "://" + page.netloc + href
            print(url)

            scraped_data.append({
                'TimeStamp': time.time(),
                'Vendor': news_source['Name'],
                'Date': date.strip(),
                'Title': title.strip(),
                'URL': url.strip(),
                'New': bool(1)
            })

# we have scraped evetything.


# we start checking if there is something new
for scraped_data_entry in scraped_data:
    for old_news_entry in old_news:
        if scraped_data_entry['Title'] == old_news_entry['Title']:
            scraped_data_entry['New'] = bool(0)

    if scraped_data_entry['New'] == bool(1):
        old_news.insert(0, scraped_data_entry)

latest_news = sorted(old_news, key=lambda x: x['TimeStamp'], reverse=True)

html_source ="""
<html><head></head><body><table>
"""

for news_entry in latest_news:
    tr = "<tr><td>"+news_entry['Date']+"</td><td>"+news_entry['Title']+"</td></tr>"
    html_source += tr

html_source +="""
</table></body></html>
"""

with open(NEWS_FILE, 'w') as f:
    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
    for row in latest_news:
        wr.writerow(row)

with open(HTML_FILE, 'w') as f:
    f.write(html_source)
