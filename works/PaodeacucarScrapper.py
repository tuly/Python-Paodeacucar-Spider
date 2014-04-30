import re
from PyQt4.QtCore import QThread, pyqtSignal
from logs.LogManager import LogManager
from utils.Csv import Csv
from utils.Utils import Utils
from spiders.Spider import Spider
from utils.Regex import Regex
from bs4 import BeautifulSoup

__author__ = 'Tuly'


class PaodeacucarScrapper(QThread):
    notifyPaode = pyqtSignal(object)

    def __init__(self):
        QThread.__init__(self)
        self.logger = LogManager(__name__)
        self.spider = Spider()
        self.regex = Regex()
        self.utils = Utils()
        self.mainUrl = 'http://www.paodeacucar.com.br/'
        self.url = 'http://www.paodeacucar.com.br/'
        dupCsvReader = Csv()
        self.dupCsvRows = dupCsvReader.readCsvRow('paodeacucar.csv', 4)
        self.csvWriter = Csv('paodeacucar.csv')
        csvDataHeader = ['SKU', 'Category', 'Subcategory', 'Name', 'URL', 'URL Image', 'Details',
                         'Nutrients Table html code', 'Price from, 28/abr/14', '28/abr/14']
        if 'URL' not in self.dupCsvRows:
            self.dupCsvRows.append(csvDataHeader)
            self.csvWriter.writeCsvRow(csvDataHeader)

    def run(self):
        self.scrapData()

    def scrapData(self):
        try:
            print 'Main URL: ', self.url
            self.notifyPaode.emit(('<font color=green><b>Main URL: %s</b></font>' % self.url))
            data = self.spider.fetchData(self.url)
            if data and len(data) > 0:
                data = self.regex.reduceNewLine(data)
                data = self.regex.reduceBlankSpace(data)
                soup = BeautifulSoup(data)
                categories = soup.find('nav', class_='items-wrapper').find_all('li', class_=re.compile('\s*item\s*'))
                print 'Total Categories: ', len(categories)
                self.notifyPaode.emit(('<font color=black><b>Total Categories: %s</b></font>' % str(len(categories))))
                for category in categories:
                    if category.a is not None:
                        submenu_target = self.regex.replaceData('#', '', category.a.get('data-target'))
                        sub_categories = soup.find('ul', id=submenu_target).find_all('li', class_='item')
                        print 'Total Sub Categories: ', len(sub_categories)
                        self.notifyPaode.emit(('<font color=black><b>Total Subcategories: %s</b></font>' % str(len(sub_categories))))
                        for sub_category in sub_categories:
                            sub_category_label = sub_category.find('span', class_='label').text
                            sub_category_url = sub_category.a.get('href') if sub_category.a is not None else 'N/A'
                            self.scrapItems(sub_category_url, category.text, sub_category_label)
        except Exception, x:
            self.logger.error(x.message)
            print x

    def scrapItems(self, url, category, sub_category, page=0):
        try:
            paginated_url = url + '?qt=36&gt=card&p=' + str(page)
            print 'Sub Category URL: ', paginated_url
            self.notifyPaode.emit(('<font color=green><b>Sub Category URL: %s</b></font>' % paginated_url))
            data = self.spider.fetchData(paginated_url)
            if data and len(data) > 0:
                data = self.regex.reduceNewLine(data)
                data = self.regex.reduceBlankSpace(data)
                data = self.regex.replaceData('<!--', '', data)
                data = self.regex.replaceData('-->', '', data)
                soup = BeautifulSoup(data)
                items = soup.find_all('div', class_=re.compile(r'(?i)boxProduct.*?'))
                print 'Total Items: ', len(items)
                self.notifyPaode.emit(('<font color=black><b>Total Items: %s</b></font>' % str(len(items))))
                for item in items:
                    product_name = item.find('h3', class_='showcase-item__name').text if item.find('h3',
                                                                                                   class_='showcase-item__name') is not None else 'N/A'
                    product_url = item.find('h3', class_='showcase-item__name').find('a', class_='link').get('href')
                    prices = item.find_all('p', class_=re.compile('(?i)showcase-item__price.*'))
                    price_de = ''
                    price_por = ''
                    if prices is not None and len(prices) > 0:
                        for price in prices:
                            if self.regex.isFoundPattern('(?i)De', price.a.text):
                                price_de = price.find('span', class_='value').text if price.find('span',
                                                                                                 class_='value') is not None else 'N/A'
                            elif self.regex.isFoundPattern('(?i)Por', price.a.text):
                                price_por = price.find('span', class_='value').text if price.find('span',
                                                                                                  class_='value') is not None else 'N/A'
                            else:
                                price_por = price.find('span', class_='value').text if price.find('span',
                                                                                                  class_='value') is not None else 'N/A'
                    print 'Product name:', product_name
                    self.notifyPaode.emit(('<font color=black><b>Product Name: %s</b></font>' % product_name))
                    thumb_image = item.find('img', class_='prdImagem img').get('src')
                    large_image = self.regex.replaceData('(?i)x\d+x\d+', '', thumb_image)

                    ## scrap others
                    product_desc, table_html = self.scrapProductdetails(product_url)

                    csv_data = ['', category, sub_category, product_name, product_url, large_image, product_desc,
                                table_html, price_de, price_por]
                    if product_url not in self.dupCsvRows:
                        print 'writing data to file...'
                        self.csvWriter.writeCsvRow(csv_data)
                        self.dupCsvRows.append(csv_data)

                    image_file_name = large_image.split('/')[-1]
                    print 'Downloading file:', image_file_name
                    self.notifyPaode.emit(('<font color=blue><b>Please wait...<br />Downloading image: %s</b></font>' % image_file_name))
                    self.notifyPaode.emit(('<font color=blue><b>Large Image URL: %s</b></font>' % large_image))
                    self.spider.downloadFile(large_image, './images/' + image_file_name)
                    self.notifyPaode.emit(('<font color=blue><b>Successfully Downloaded image: %s</b></font>' % image_file_name))

                    if soup.find('li', class_='pageSelect nextPage item inline--middle').find('a') is not None:
                        return self.scrapItems(url, category, sub_category, (page + 1))
        except Exception, x:
            self.logger.error(x.message)
            print x

    def scrapProductdetails(self, url):
        description = ''
        table_html = ''
        try:
            print 'Product URL: ', url
            self.notifyPaode.emit(('<font color=green><b>Product Details URL: %s</b></font>' % url))
            data = self.spider.fetchData(url)
            if data and len(data) > 0:
                data = self.regex.reduceNewLine(data)
                data = self.regex.reduceBlankSpace(data)
                data = self.regex.replaceData('<!--', '', data)
                data = self.regex.replaceData('-->', '', data)
                soup = BeautifulSoup(data)
                description = soup.find('div', class_='product-info__text').text
                table_html = soup.find('table', class_='product-grid__table')
        except Exception, x:
            self.logger.error(x.message)
            print x
        return description, table_html
