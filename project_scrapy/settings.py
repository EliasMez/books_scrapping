# Scrapy settings for project_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

BOT_NAME = 'project_scrapy'

SPIDER_MODULES = ['project_scrapy.spiders']
NEWSPIDER_MODULE = 'project_scrapy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'project_scrapy (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# delay aleatoire entre 0.5 et 1.5 mutltiplié par DOWNLOAD_DELAY
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'fr-FR,fr',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'project_scrapy.middlewares.ProjectScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
    # gérer les requêtes via leur service de proxy (scrapeops par défaut)
    'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': None,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # gère la configuration des proxies HTTP pour les requêtes.
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    # gère les tentatives de nouvelles requêtes en cas d'échec (middleware scrapy par défaut)
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'project_scrapy.middlewares.ScrapeOpsFakeBrowserHeadersMiddleware': 400,
    # 'project_scrapy.middlewares.ScrapeOpsFakeUserAgentMiddleware': 500,
    'project_scrapy.middlewares.ScrapeOpsProxyMiddleware': 600,
    # gère les tentatives de nouvelles requêtes en cas d'échec
    'scrapeops_scrapy.middleware.retry.RetryMiddleware': 800,
    # empêche le crawler de suivre des liens vers des domaines qui ne sont pas listés dans allowed_domains du spider.
    'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': None, 
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
   'scrapeops_scrapy.extension.ScrapeOpsMonitor': 700, 
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'project_scrapy.pipelines.ProjectScrapyPipeline': 200,
    'project_scrapy.pipelines.DataBasePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'





SCRAPEOPS_API_KEY = API_KEY
SCRAPEOPS_PROXY_SETTINGS = {'country': 'us', 'js_scenario': False, 'session_number': False}
SCRAPEOPS_NUM_RESULTS = 100

SCRAPEOPS_FAKE_USER_AGENT_ENABLED = False
SCRAPEOPS_FAKE_HEADERS_ENABLED = False
SCRAPEOPS_PROXY_ENABLED = True

SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT = 'http://headers.scrapeops.io/v1/user-agents?'
SCRAPEOPS_FAKE_HEADERS_ENDPOINT = 'http://headers.scrapeops.io/v1/browser-headers?'
SCRAPEOPS_FAKE_PROXY_ENDPOINT = 'https://proxy.scrapeops.io/v1/?'
SCRAPEOPS_FAKE_PROXY_ENDPOINT = 'https://proxy.scrapeops.io/v1/?'
