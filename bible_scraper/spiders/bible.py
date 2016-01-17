import scrapy
from scrapy.exceptions import CloseSpider
import sys
import json
import urllib
import os
from threading import Thread
import logging

def join_verse(verse):
    return ''.join(verse)

def get_xpath(response, xpath):
    return response.xpath(xpath).extract()

def get_last_verse(response, index):
    chapter_length = response.xpath('//span[@class="label"]//text()').extract()[index]
    if chapter_length != "#":
        return chapter_length
    else:
        return get_last_verse(response, index-1)

class BibleSpider(scrapy.Spider):

    name = "bible"
    allowed_domains = ["bible.com"]

    base_link = "http://bible.com"

    output = {}

    # pass version in crawl command. e.g. scrapy crawl bible -a version=111
    def __init__(self, version=''):
        self.start_urls = ['https://www.bible.com/bible/%s/gen.1' % version]


    def write_file(self):
        with open("output.json", 'w+') as test:
            json.dump(self.output, test, indent=4, sort_keys=True)

    def parse(self, response):

        '''
        TODO: Get chapter number from site.
        Book name: response.xpath('//a[@id="reader_book"]/text()').extract()
        Chapter:
        '''
        book = response.xpath('//a[@id="reader_book"]/text()').extract()[0]
        if book not in self.output:
            self.output[book] = {}

        chapter = response.xpath('//a[@id="reader_chapter"]/text()').extract()[0]
        if chapter not in self.output[book]:
            self.output[book][chapter] = {}

        chapter_length = get_last_verse(response, -1)

        verse_string= '//span[@class="verse v%s"]/span[@class="content" or @class="wj"]//text()'
        for i in range(1, int(chapter_length) + 1):
            extract_string = verse_string % i
            # xpath expression returns the verse in a list.
            verse = join_verse(get_xpath(response, extract_string))
            self.output[book][chapter][i] = verse

        if book == "Revelation" and chapter == "22":
            download_thread = Thread(target = self.write_file)
            download_thread.start()
            raise CloseSpider("End of Bible")
        else:
            next_chapter = self.base_link + response.xpath('//a[@id="reader_next"]/@href').extract()[0]
            yield scrapy.Request(next_chapter, callback=self.parse)

class BibleMp3Spider(scrapy.Spider):
    name = "bible_mp3"
    allowed_domains = ["bible.com"]

    base_link = "http://bible.com"

    book_index = 1

    def __init__(self, version=''):
        self.start_urls = ['https://www.bible.com/bible/%s/gen.1' % version]
        self.version = version

    output = {}

    # Thread function for downloading mp3
    def download_mp3(self, mp3_url, filename, folder):

        directory = os.getcwd() + folder
        logging.log(logging.WARNING, os.getcwd())
        logging.log(logging.WARNING, "THIS IS THE FOLDER: " + directory)
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.download_mp3(mp3_url, filename, folder)
            return
        else:
            filename = os.path.join(directory, filename)

        urllib.urlretrieve (mp3_url, filename)
        self.book_index += 1

    def get_folder(self, url):
        split = self.version + "/"
        folder = url.split(split)[1]
        folder = folder.split('.')[0]
        return "/" + folder


    def parse(self, response):
        book = response.xpath('//a[@id="reader_book"]/text()').extract()[0]
        chapter = response.xpath('//a[@id="reader_chapter"]/text()').extract()[0]

        if "intro" not in response.url:
            #Get mp3 link
            mp3_url = response.xpath('//audio[@id="reader_audio_player"]/@src').extract()[0]
            mp3_url = mp3_url.split("?", 1)[0]
            mp3_url = "http:" + mp3_url

            folder = self.get_folder(response.url)
            filename = chapter + folder.strip('/') + ".mp3"
            folder = folder + "/"
            download_thread = Thread(target = self.download_mp3, args = (mp3_url, filename, folder))
            download_thread.start()

        if book == "Revelation" and chapter == "22":
            raise CloseSpider("End of Bible")
        else:
            next_chapter = self.base_link + response.xpath('//a[@id="reader_next"]/@href').extract()[0]
            yield scrapy.Request(next_chapter, callback=self.parse)
