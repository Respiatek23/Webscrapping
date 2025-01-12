import sys
from Spyder import procesar_borme as execute_spider
from Fetcher import execute as execute_fetcher
from Crawler import run as execute_crawler
from Wrangler import run as execute_wrangler
if __name__ == "__main__":
 arguments = sys.argv
 if "SPIDER" in arguments:
 	execute_spider(arguments[-1])
 if "FETCHER" in arguments:
  	execute_fetcher()
 if "CRAWLER" in arguments:
 	execute_crawler()
 if "WRANGLER" in arguments:
 	execute_wrangler()



