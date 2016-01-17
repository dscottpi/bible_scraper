# bible_scraper
Scrapy spider for crawling the bible from bible.com

See http://scrapy.org for how to set up scrapy. 

###There are two available spiders:

  **bible_mp3**: downloads the audio of each chapter in the bible. (saved in mp3).
  
  **bible**: crawls the entire bible and saves the output in a json file. 

###To run the spider: 

You need the Bible Version code from the bible.com site, e.g. NIV URL would be: 

https://www.bible.com/en-GB/bible/111/gen.1 -  and the 111 being the version.

Then simply run: 
```python
scrapy crawl {spider_name} -a version={version_code}
```
