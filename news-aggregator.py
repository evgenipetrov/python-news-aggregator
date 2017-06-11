import json
import subprocess
from urllib import parse

import validators
from lxml import html

CONFIG_FILE = 'config.json'


def uri_validator(x):
    try:
        result = urlparse(x)
        return True if [result.scheme, result.netloc, result.path] else False
    except:
        return False


with open(CONFIG_FILE) as data_file:
    data = json.load(data_file)

newsSources = data['newsSources']

for newsSource in newsSources:

    bashCommand = 'phantomjs fetchPage.js ' + newsSource['Url']
    print(bashCommand)

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)  # , cwd='path\to\somewhere')
    output, error = process.communicate()
    # print('out', output)
    print('err', error)

    fileName = '/tmp/' + (newsSource['Name'] + '.html').lower()
    file = open(fileName, "w")
    file.write(str(output, 'utf-8'))
    file.close()

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
