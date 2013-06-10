from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.spiders.init import InitSpider
from kaufman.items import ForumPost
from scrapy.selector import HtmlXPathSelector
import urlparse, re
from datetime import date, datetime, timedelta

class KaufspiderSpider(CrawlSpider, InitSpider):
    name = 'kaufspider'
    allowed_domains = ['familykaufman.forumotion.com']
    login_page = 'http://familykaufman.forumotion.com/login'
    start_urls = ['http://familykaufman.forumotion.com/f1-kaufman-family-discussion']

    rules = (
        Rule(SgmlLinkExtractor(allow=('', )), callback='parse_post', process_links='get_topic_links', follow=True),
        Rule(SgmlLinkExtractor(allow=('', )), callback='parse_post', process_links='get_page_links', follow=True),
        
    )
    
    def init_request(self):
        return Request(url=self.login_page, callback=self.login)
    
    def login(self, response):
        return FormRequest.from_response(response,
            formname = 'form_login',
            
            #Put a working username/password combination here to use!
            formdata = {'username': '***REMOVED***', 'password': '***REMOVED***'},
            
            callback=self.check_login_response)
    
    def check_login_response(self, response):
        if not "Your last visit" in response.body:
            self.log("Login failed", level=log.ERROR)
            return
        else:
            self.log("Login successful")
            return self.initialized()
        
    def get_page_links(self, links):
        return [link for link in links if self.is_page_link(link)]
    
    def get_topic_links(self, links):
        return [link for link in links if self.is_topic_link(link)]
    
    def is_page_link(self, link):
        parsed = urlparse.urlparse(link.url)
        querydict=urlparse.parse_qs(parsed.query)
        
        #only follow links of the form "t[num]p[num]-" and exclude abuse report / topic watch links
        stopwords = ['abuse', 'watch', 'unwatch']
        return all(x not in querydict for x in stopwords) and re.match('t\d+-.*', parsed.path)
    
    def is_topic_link(self, link):
        parsed = urlparse.urlparse(link.url)
        querydict=urlparse.parse_qs(parsed.query)
        
        #only follow links of the form "t[num]-" and exclude abuse report / topic watch links
        stopwords = ['abuse', 'watch', 'unwatch']
        return all(x not in querydict for x in stopwords) and re.match('/t\d+p\d+-.*', parsed.path)
        

    def parse_post(self, response):
        if not "Log out" in response.body:
            self.login()
        
        forumposts = []
        hxs = HtmlXPathSelector(response)
        title = hxs.select('/html/head/title/text()').extract()[0]
        self.log('Followed a link to page: %s' % title)
        posts = hxs.select('//div[@class=\'postbody\']')
        self.log("Found %d posts" % len(posts))
        
        for post in posts:
            forumpost = ForumPost()
            forumpost['subforum'] = re.sub(' - Page \d+$', '', title)
            forumpost['username'] = post.select('p/a/text()').extract()
            thistime = post.select('p/text()[2]').extract()[0]
            forumpost['time'] = self.parse_date(thistime)
            forumpost['text'] = post.select('div[3]/div/text()').extract()
            forumposts.append(forumpost)
        return forumposts
    
    def parse_date(self, datestring):
        datestring = datestring.replace("Today",date.today().isoformat())
        datestring = datestring.replace("Yesterday",(date.today()-timedelta(days=1)).isoformat())
        datestring = datestring.replace(" at ",", ")
        datestring = datestring.strip('on ,')
        return datetime.strptime(datestring, '%Y-%m-%d, %H:%M')
        
