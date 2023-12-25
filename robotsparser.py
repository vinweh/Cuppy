from urllib.parse import urlparse
from contextlib import closing
from customrobotsparser import CustomRobotParser
from cuppydb import CuppyDatabase


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
        Initialize the RobotsTxtParser object.
        
        Parameters:
        - cache_db_conn: The connection to the CuppyDatabase object representing the cache database.
        """
        self.parser = CustomRobotParser()
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
        
        Get a list of sitemap URLs specified in the robots.txt file.
        
        Returns:
        - A list of sitemap URLs.
        """
        return self.parser.site_maps()
    

def robots_location(url) -> str:
    """Get the presumed location of robots.txt
    
    Get the presumed location of the robots.txt file based on the given URL.
    
    Parameters:
    - url: The URL for which the robots.txt location is determined.
    - root: Whether to include the root URL in the result. Default is False.
    
    Returns:
    - The presumed location of the robots.txt file.
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
    