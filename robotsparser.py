from urllib.parse import urlparse
import urllib.request
from contextlib import closing

from cuppydb import CuppyDatabase
from protego import Protego


class RobotsTxtCache:
    """Class to cache robots.txt files
    
    This class provides methods to cache and retrieve robots.txt content.
    It uses a SQLite database to store the cached content.
    """
    def __init__(self, db: CuppyDatabase):
        """
        Initialize the RobotsTxtCache object.
        
        Parameters:
        - db: CuppyDatabase object representing the SQLite database connection.
        """
        self.db = db
        self.db.execute_query("CREATE TABLE IF NOT EXISTS robots_txt (url TEXT PRIMARY KEY, content TEXT)")
        
    
    def get(self, url):
        """Get robots.txt content from cache
        
        Retrieve the robots.txt content from the cache based on the given URL.
        
        Parameters:
        - url: The URL of the robots.txt file.
        
        Returns:
        - The content of the robots.txt file if found in the cache, None otherwise.
        """
        row = self.db.fetch_one("SELECT content FROM robots_txt WHERE url = ?", (url,))
        
        if row:
            return row[0]
        else:
            return None
    
    def put(self, url, content):
        """Put robots.txt content into cache
        
        Store the robots.txt content in the cache for the given URL.
        If the URL already exists in the cache, the content will be updated.
        
        Parameters:
        - url: The URL of the robots.txt file.
        - content: The content of the robots.txt file.
        """
        upsert_query = """
        INSERT INTO robots_txt (url, content) VALUES (?, ?) 
        ON CONFLICT(url) DO UPDATE SET content=? WHERE url=?"""

        self.db.execute_query(upsert_query, (url, content, content, url))
        
class RobotsTxtParser:
    """Encapsulates a robots.txt parser
    """
    def __init__(self, cache_db_conn):
        """
        Initialize the RobotsTxtParser object.
        
        Parameters:
        - cache_db_conn: The connection to the CuppyDatabase object representing the cache database.
        """
        self._parser = None
        self.robots_content = None
        self.robot_cache = RobotsTxtCache(cache_db_conn)
        
    def read_from_cache(self, url):
        """Read robots.txt from cache
        
        Read the robots.txt content from the cache based on the given URL.
        
        Parameters:
        - url: The URL of the robots.txt file.
        
        Returns:
        - The content of the robots.txt file if found in the cache, None otherwise.
        """
        return self.robot_cache.get(url)
    
    def read_from_url(self, url):
        """Read robots.txt from URL
        
        Read the robots.txt content from the given URL.
        
        Parameters:
        - url: The URL of the robots.txt file.
        
        Returns:
        - The content of the robots.txt file if found, None otherwise.
        """
        try:
            with closing(urllib.request.urlopen(url)) as f:
                raw = f.read()
                return raw.decode("utf-8")
        except Exception as e:
            print(f"Error: {e}")
            return None

    def can_fetch(self, url, user_agent="*"):
        """Get verdict for a URL, user-agent combination
        
        Check if the given URL is allowed to be fetched by the specified user agent
        based on the robots.txt rules.
        
        Parameters:
        - url: The URL to be checked.
        - user_agent: The user agent string. Default is "*".
        
        Returns:
        - True if the URL is allowed to be fetched, False otherwise.
        """
        can_fetch = False
        robots_url = robots_location(url)
        robots_from_cache = self.read_from_cache(robots_url)
        if robots_from_cache:
            self._parser = Protego.parse(robots_from_cache)
            can_fetch = self._parser.can_fetch(user_agent, url)
        else:
            self.robots_content = self.read_from_url(robots_url)
            if self.robots_content:
                self._parser = Protego.parse(self.robots_content)
                self.robot_cache.put(robots_url, self.robots_content)
                can_fetch = self._parser.can_fetch(user_agent, url)
            else:
                print(f"Error: robots.txt not found at {robots_url}")
                can_fetch = False
        return can_fetch

    @property
    def sitemaps(self):
        """Get sitemaps from robots.txt
        
        Returns:
        - A list of sitemap URLs.
        """
        return self._parser.sitemaps

    @property
    def crawl_delay(self, user_agent="*"):
        """Get crawl delay from robots.txt
        
        Parameters:
        - user_agent: The user agent string. Default is "*".
        
        Returns:
        - The crawl delay in seconds.
        """
        return self._parser.crawl_delay(user_agent)
    
    @property
    def request_rate(self, user_agent="*"):
        """Get request rate from robots.txt
        
        Parameters:
        - user_agent: The user agent string. Default is "*".
        
        Returns:
        - The request rate in seconds.
        """
        return self._parser.request_rate(user_agent)

def robots_location(url) -> str:
    """Get the presumed location of robots.txt

    Determine the URL of the ``robots.txt`` file for the provided address.

    Parameters:
    - url: The URL for which the robots.txt location is determined.

    Returns:
    - The presumed location of the robots.txt file.
    """
    robots = "robots.txt"
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    url = f"{parsed_url.scheme}://{domain}/{robots}"
    return url

if __name__ == "__main__":
    
    #url = "https://aws.amazon.com/partners/work-with-partners/?nc2=h_ql_pa_wwap_cp"
    url = "https://www.google.com"
    db = CuppyDatabase("cuppy-dev.db")
    db.connect()
    rp = RobotsTxtParser(db)
    print(rp.can_fetch(url, "*"))
    print(rp.crawl_delay("*")) 
    for s in rp.sitemaps:
        print(s)
    
    db.disconnect()
    