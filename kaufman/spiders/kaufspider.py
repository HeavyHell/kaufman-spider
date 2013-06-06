from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.spiders.init import InitSpider
from kaufman.items import ForumPost
from scrapy.selector import HtmlXPathSelector
import urlparse, re

class KaufspiderSpider(CrawlSpider, InitSpider):
    name = 'kaufspider'
    allowed_domains = ['familykaufman.forumotion.com']
    login_page = 'http://familykaufman.forumotion.com/login'
    start_urls = ['http://familykaufman.forumotion.com/f1-kaufman-family-discussion']

    rules = (
        Rule(SgmlLinkExtractor(allow=('', )), callback='parse_post', process_links='get_page_links', follow=True),      
        
    )
    
    def init_request(self):
        return Request(url=self.login_page, callback=self.login)
    
    def login(self, response):
        return FormRequest.from_response(response,
            formname = 'form_login',
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
    
    def is_page_link(self, link):
        parsed = urlparse.urlparse(link.url)
        querydict=urlparse.parse_qs(parsed.query)
        
        #only follow only links of the form "t[num]-" or "t[num]p[num]-, and exclude abuse report / topic watch links
        stopwords = ['abuse', 'watch', 'unwatch']
        return all(x not in querydict for x in stopwords) and re.match('/t\d+p\d+-.*|t\d+-.*', parsed.path)
        

    def parse_post(self, response):
        
        forumposts = []
        hxs = HtmlXPathSelector(response)
        title = hxs.select('/html/head/title/text()').extract()
        self.log('Followed a link to page: %s' % title)
        posts = hxs.select('//div[@class=\'postbody\']')
        self.log("Found %d posts" % len(posts))
        
        for post in posts:
            forumpost = ForumPost()
            forumpost['subforum'] = title
            forumpost['username'] = post.select('p/a/text()').extract()
            forumpost['time'] = post.select('p/text()[2]').extract()
            forumpost['text'] = post.select('div[3]/div/text()').extract()
            forumposts.append(forumpost)
        return forumposts
        
