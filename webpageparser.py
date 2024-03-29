import os, sys
import argparse
from urllib.parse import urlparse
import requests
from cuphtmlparser import CupHTMLParser
from cuppydb import CuppyDatabase
from robotsparser import RobotsTxtParser
from htmlcleaner import HTMLCleaner


class WebpageParser:
    """Class to parse a list of URLs and extract metadata and mores from headers and/or HTML content"""
    def __init__(self, urls: list[str], robotstxt: bool = False, force: bool = False):

        self.urls = urls
        self.url = None
        self.etag = None
        self.status_code = None
        self.html_parser = CupHTMLParser()
        self.content = None
        self.headers = None
        self.title = None
        self.og_url = None
        self.og_title = None
        self.canonical_url_from_headers = None
        self.canonical_url_from_html = None
        self.description = None
        self.clean_text = None
        self.db = CuppyDatabase("cuppy-dev.db")
        self.db.connect()
        self.success_count = 0
        self.run_id = None
        self.robotstxt = robotstxt
        self.force = force
        self.user_agent = os.environ.get("USER_AGENT", "CUPPy/0.1")

    def reset(self):
        """Reset all attributes to None"""
        self.etag = None
        self.content = None
        self.headers = None
        self.status_code = None
        self.title = None
        self.canonical_url_from_headers = None
        self.canonical_url_from_html = None
        self.og_title = None
        self.og_url = None
        self.description = None
        self.clean_text = None
        self.html_parser = CupHTMLParser()
        
  
    def parse(self):
        """Parse all URLs in list
        """
        for url in self.urls:
            self.url = url
            self.parse_url()
            self.write_results_to_database()
            self.reset() # reset attributes for next URL
    
    def get_etag_from_cache(self):
        """Get etag from the database/cache""" 
        select_data_query = """
        SELECT etag FROM urls WHERE url = ?;"""
        row = self.db.fetch_one(select_data_query, (self.url,))
        if row:
            return row[0]
        else:
            return None

    def parse_url(self):
        """Parse a single URL"""
        self.get_webpage()
        if self.status_code == requests.codes.ok:
            self.get_canonical_from_headers()
            self.get_metadata_from_html()
            self.get_clean_text()
         
    def get_webpage(self):
        """Get webpage and store status code, content and headers"""
        print(f"Getting webpage: {self.url}")
        
        headers = {'user-agent': self.user_agent
                   ,'Accept' : 'text/html'}
        
        if not self.force:
            cached_etag = self.get_etag_from_cache()
            if cached_etag:
                headers['If-None-Match'] = cached_etag
                print(f"Using cached etag: {cached_etag}")
        else:
            print("Forcing refetch, not looking for cached etag (if any)")
                    
        if self.robotstxt:
            rp = RobotsTxtParser(self.db)
            if rp.can_fetch(self.url, '*'):
                print(f"Success: robots.txt allows {self.url}")               
            else:
                print(f"Error: robots.txt disallows {self.url}")
                self.reset()
                return
        try:
            r = requests.get(self.url, headers=headers)
            self.etag = r.headers.get("etag")
            self.status_code = r.status_code
            if self.status_code == requests.codes.ok:
                print(f"Success: status code {self.status_code}")
                self.content = r.content
                self.headers = r.headers
            elif not self.force and self.status_code == requests.codes.not_modified:
                print(f"Not modified: status code {self.status_code}")
            else:
                print(f"Error: status code {self.status_code}")
                self.reset()
        except Exception as e:
            print(f"Error: {e}")
            self.reset()

    def get_canonical_from_headers(self):
        """Extract canonical URL from HTTP headers"""
        link_header = self.headers.get("link")
        if link_header:
            links = link_header.split(",") # can be multiple links
            for link in links:
                if link.find("canonical") > -1:
                    self.canonical_url_from_headers = link.split(";")[0].strip("<>")
                   
    def get_metadata_from_html(self):
        """Extract meta data from HTML content"""
        if self.content:
            html = self.content.decode("utf-8")
            self.html_parser.feed(html)
            self.canonical_url_from_html = self.html_parser.canonical_url
            self.og_url = self.html_parser.og_url    
            self.title = self.html_parser.title
            self.og_url = self.html_parser.og_url
            self.description = self.html_parser.description
           
        else:
            print(f"Error: no HTML content")

    def get_clean_text(self):
        """Get clean text from HTML content"""
        if self.content:
            html = self.content.decode("utf-8")
            self.clean_text = HTMLCleaner.clean_text(html)
        else:
            print(f"Error: no HTML content")
    
    def write_results_to_database(self):
        """Write results to database"""
        if self.status_code == requests.codes.ok: #for now
            insert_data_query = """
            INSERT INTO urls (url, etag, status_code, timestamp, title, canonical_url_header
            , canonical_url_html, og_url, og_title, description, clean_text)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET 
                etag = ?,
                status_code = ?,
                timestamp = CURRENT_TIMESTAMP,
                title = ?,
                canonical_url_header = ?,
                canonical_url_html = ?,
                og_url = ?,
                og_title = ?,
                description = ?,
                clean_text = ?
            WHERE url = ?;
            """
            data = (
                self.url,
                self.etag,
                self.status_code,
                self.title,
                self.canonical_url_from_headers,
                self.canonical_url_from_html,
                self.og_url,
                self.og_title,
                self.description,
                self.clean_text,
                self.etag,
                self.status_code,
                self.title,
                self.canonical_url_from_headers,
                self.canonical_url_from_html,
                self.og_url,
                self.og_title,
                self.description,
                self.clean_text,
                self.url
            )
            self.db.execute_query(insert_data_query, data)
        elif self.status_code == requests.codes.not_modified:
            print(f"Not modified so not updating db. Status code {self.status_code}")
    
        else:
            # to do error table 
            print(f"Error: status code {self.status_code}")
        
        
        
def get_urls_from_file(filename: str) -> list[str]:
    """Get URLs from file"""
    with open(filename, "r") as f:
        urls = f.read().splitlines()
    return [u for u in urls if is_valid_url(u)] # filter out invalid

def is_valid_url(url: str) -> bool:
    """Check if URL is 'valid', ie. has scheme and netloc"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
    
    
def main(url_file: str, robotstxt: bool = False, force: bool = False):
    """Main function
    :param url_file: file containing URLs, one per line
    """
    urls = get_urls_from_file(url_file)
    cup  = WebpageParser(urls
                        ,robotstxt=robotstxt
                        ,force=force)
    cup.parse()
    

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Parse URLs and extract canonical URL from headers and/or HTML content")
    argparser.add_argument("url_file"
                           , help="File containing URLs, one per line.")
    argparser.add_argument("-r", "--robotstxt", action="store_true"
                           , help="Check robots.txt before parsing URL")
    argparser.add_argument("-f", "--force", action="store_true"
                           , help="Force refetch of URL even if etag matches")
    args = argparser.parse_args()
    sys.exit(main(args.url_file, robotstxt=args.robotstxt, force=args.force))