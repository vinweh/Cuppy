import requests
from bs4 import BeautifulSoup

class HTMLCleaner:
    """Class to clean HTML of elements that do not contain 'main content'"""
    @staticmethod
    def remove_all_nav(soup, removables=[]):
        """Remove known nav, header, footer, and other nav stuff from soup"""
        elements = soup.select(", ".join(removables))
        for elem in elements:
            if elem.name == "header" and elem.parent.name in ("article", "main"):
                continue
            elem.decompose()
        return soup

    @staticmethod
    def stripped(content, custom_removables=[]):
        removables = ["nav", 
                      "header", 
                      "footer", 
                      "head", 
                      "*[style='display:none']",
                      "*[style='display: none;']",  
                      "*[role='navigation']"
                      ,"*[aria-hidden='true']"]
        removables.extend(custom_removables)
        soup = BeautifulSoup(content, 'lxml')
        HTMLCleaner.remove_all_nav(soup, removables)
        return(" ".join(" ".join(t.strip().split()) \
                        for t in soup.stripped_strings if t.strip() != ""))
        

if __name__ == "__main__":
    
    #url = "https://www.cnn.com/2023/12/25/travel/blizzard-nebraska-south-dakota-colorado-travel-delays/index.html"
    #url = "https://scrapeops.io/blog/the-state-of-web-scraping-2022/"
    #url = "https://www.japan-guide.com/e/e3034_001.html"
    #url = "https://www.youtube.com/watch?v=WMp3EbI0bU4" #will not work, use API
    #url = "https://en.wikipedia.org/wiki/Bothell%2C_Washington"
    # You can pass in custom list of elements to remove, here is an example for wikipedia and stackoverflow
    #custom_removables = ['div.reflist', '.vector-dropdown-content', '.uls-lcd-region-section']
    #url = "https://stackoverflow.com/questions/3379166/writing-blob-from-sqlite-to-file-using-python"
    #custom_removables = ['#answers-header', '#sidebar', '#post-form', '.bottom-notice']
    url = "https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_9069952433271538175%22%7D&n_type=1&p_from=3"
    html = requests.get(url).text
    print(f"HTML length: {len(html)}")
    soup = BeautifulSoup(html, 'lxml')
    text = HTMLCleaner.stripped(html)
    print(f"Clean text length: {len(text)}")
    print(f"Clean text length in bytes: {len(text.encode('utf-8'))}")
    with open("stripped.txt", "w", encoding='utf-8') as f:
        f.write(text)