#from urllib import robotparser
from urllib.parse import urlparse
import sqlite3
from contextlib import closing
from customrobotsparser import CustomRobotParser
from cuppydb import CuppyDatabase


class RobotsTxtCache:
    """Class to cache robots.txt files
    """
    def __init__(self, db: CuppyDatabase):
        
        self.db = db
        self.db.execute_query("CREATE TABLE IF NOT EXISTS robots_txt (url TEXT PRIMARY KEY, content TEXT)")
        
    
    def get(self, url):
        """Get robots.txt content from cache
        """
        row = self.db.fetch_one("SELECT content FROM robots_txt WHERE url = ?", (url,))
        
        if row:
            return row[0]
        else:
            return None
    
    def put(self, url, content):
        """Put robots.txt content into cache
        """
        upsert_query = """
        INSERT INTO robots_txt (url, content) VALUES (?, ?) 
        ON CONFLICT(url) DO UPDATE SET content=? WHERE url=?"""

        self.db.execute_query(upsert_query, (url, content, content, url))
        
class RobotsTxtParser:
    """Encapsulates a robots.txt parser. Note that this
    is a wrapper around the standard library robotparser, which
    interprets robots.txt rules differently than e.g. Googlebot 
    or Bingbot. Specifically, the standard library parser does not
    support the Allow directive in the same way as Googlebot or Bingbot.
    A first-found Disallow: rule wins over a later Allow: rule.

    There are better parsers out there, such as reppy by (Seo)Moz or Portego (#TODO)
    """
    def __init__(self, cache_db_conn):
        """
        """
        self.parser = CustomRobotParser()
        self.robot_cache = RobotsTxtCache(cache_db_conn)
        
    def read_from_cache(self, url):
        """Read robots.txt from cache
        """
        return self.robot_cache.get(url)

    def can_fetch(self, url, user_agent="*"):
        """Get verdict for a URL, user-sagent combination
        """
        robots_url = robots_location(url)
        robots_from_cache = self.read_from_cache(robots_url)
        if robots_from_cache:
            self.parser.parse(robots_from_cache.splitlines())
        else:
            self.parser.set_url(robots_url)
            self.parser.read()
            self.robot_cache.put(robots_url, self.parser.robots_content)
        return self.parser.can_fetch(user_agent, url)
    
    def get_sitemaps(self) -> list[str]:
        """Get list of sitemaps
        """
        return self.parser.site_maps()
    

def robots_location(url) -> str:
    """Get the presumed location of robots.txt
        """
    robots = "robots.txt"
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    url = f"{parsed_url.scheme}://{domain}/{robots}"
    return url

if __name__ == "__main__":
    
    url = "https://aws.amazon.com/partners/work-with-partners/?nc2=h_ql_pa_wwap_cp"
    db = CuppyDatabase("cuppy-dev.db")
    db.connect()
    rp = RobotsTxtParser(db)
    print(rp.can_fetch(url, "*"))
    print(rp.get_sitemaps())
    db.disconnect()
    