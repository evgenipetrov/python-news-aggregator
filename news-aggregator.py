import json
import subprocess
import validators
import time
import csv
import datetime

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
    #with open(file, newline='') as f:
    #    reader = csv.reader(f, delimiter=' ', quotechar='|')
    #    for row in reader:
    #        output.append(row)
    with open(file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            output.append(row)
    return output

#def save_latest_news(news):



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
            news_date = newsItem.xpath(news_source['ExtractionRules']['Date'])[0].text
            if news_date is None:
                news_date = '-'
            print(news_date)
            news_title = newsItem.xpath(news_source['ExtractionRules']['Title'])[0].text
            if news_title is None:
                news_title = '-'
            print(news_title)
            href = newsItem.xpath(news_source['ExtractionRules']['Address'])[0].attrib['href']
            if (validators.url(href)):
                news_url = href
            else:
                page = parse.urlparse(news_source['Url'])
                if not (href.startswith('/')):
                    href = '/' + href
                news_url = page.scheme + "://" + page.netloc + href
            if news_url is None:
                news_url = '-'
            print(news_url)

            timestamp = int(time.time())
            vendor = news_source['Name']
            #if not news_date == '':
            #    news_date.strip()
            if not news_title == '':
                news_title.strip()
            if not news_url == '':
                news_url.strip()

            scraped_data.append({
                'TimeStamp': timestamp,
                'Vendor': vendor,
                'Date': news_date,
                'Title': news_title,
                'URL': news_url,
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

latest_news = sorted(old_news, key=lambda x: int(x['TimeStamp']), reverse=True)

html_source ="""
<!DOCTYPE html>
<html lang="en">
    <head>
         <!-- Latest compiled and minified CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        
        <!-- jQuery library -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        
        <!-- Latest compiled JavaScript -->
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script> 
    </head>
<body><table>
<tr>
    <th>Imported</th><th>Vendor</th><th>Publish date</th><th>News</th>
</tr>
"""

for news_entry in latest_news:
    imported = datetime.datetime.fromtimestamp(float(news_entry['TimeStamp'])).strftime('%c')
    vendor = news_entry['Vendor']
    date = news_entry['Date']
    a = "<a href=\""+news_entry['URL']+"\" target=\"_blank\">"+news_entry['Title']+"</a>"
    tr = "<tr><td>"+imported+"</td><td>"+vendor+"</td><td>"+date+"</td><td>"+a+"</td></tr>"
    html_source += tr

html_source +="""
</table></body></html>
"""

with open(NEWS_FILE, 'w', newline='') as f:
    keys = latest_news[0].keys()
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(latest_news)

soup=BeautifulSoup(html_source, "lxml")                #make BeautifulSoup
prettyHTML=soup.prettify()

with open(HTML_FILE, 'w') as f:
    f.write(prettyHTML)
