# Scrapy settings for kaufman project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'kaufman'

SPIDER_MODULES = ['kaufman.spiders']
NEWSPIDER_MODULE = 'kaufman.spiders'
DOWNLOAD_DELAY = 1.25
ITEM_PIPELINES = ['kaufman.pipelines.KaufmanPipeline']

DATABASE = {'drivername': 'postgres',
            'host': 'host',
            'port': 'post',
            'username': 'username',
            'password': 'password',
            'database': 'scrape'}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'kaufman (+http://www.yourdomain.com)'
