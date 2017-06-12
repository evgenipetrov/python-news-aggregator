import json
import subprocess
import validators
import time

from urllib import parse
from lxml import html
from pyvirtualdisplay import Display
from selenium import webdriver


CONFIG_FILE = 'config.json'


def uri_validator(x):
    try:
        result = urlparse(x)
        return True if [result.scheme, result.netloc, result.path] else False
    except:
        return False


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


with open(CONFIG_FILE) as data_file:
    data = json.load(data_file)

newsSources = data['newsSources']

for newsSource in newsSources:
    if newsSource['Fetch'] == "true":

        #output = get_page_phantomjs(newsSource['Url'])
        output = get_page_firefox(newsSource['Url'])

        save_page_source(output)

        newsItems = html.fromstring(output).xpath(newsSource['PreExtractionRules'])

        for newsItem in newsItems:
            date = newsItem.xpath(newsSource['ExtractionRules']['Date'])[0].text
            print(date)
            title = newsItem.xpath(newsSource['ExtractionRules']['Title'])[0].text
            print(title)
            href = newsItem.xpath(newsSource['ExtractionRules']['Address'])[0].attrib['href']
            if (validators.url(href)):
                url = href
            else:
                page = parse.urlparse(newsSource['Url'])
                if not (href.startswith('/')):
                    href = '/' + href
                url = page.scheme + "://" + page.netloc + href
            print(url)

