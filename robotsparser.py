from urllib import robotparser
from urllib.parse import urlparse

class RobotsTxtParser:
    """Encapsulates a robots.txt parser. Note that this
    is a wrapper around the standard library robotparser, which
    interprets robots.txt rules differently than e.g. Googlebot 
    or Bingbot. Specifically, the standard library parser does not
    support the Allow directive in the same way as Googlebot or Bingbot.
    A first-found Disallow: rule wins over a later Allow: rule.

    There are better parsers out there, such as reppy by (Seo)Moz.
    """
    def __init__(self, robots_txt_url):
        """
        """
        self.parser = robotparser.RobotFileParser()
        self.parser.set_url(robots_txt_url)
        self.parser.read()

    def can_fetch(self, url, user_agent="*"):
        """Get verdict for a URL, user-sagent combination
        """
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
    robots_url = robots_location(url)
    rp = RobotsTxtParser(robots_url)
    print(rp.can_fetch(url, "*"))
    print(rp.get_sitemaps())