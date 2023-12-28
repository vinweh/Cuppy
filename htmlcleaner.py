import requests
from bs4 import BeautifulSoup

removables = ["nav", 
                      "header", 
                      "footer", 
                      "head", 
                      "*[style='display:none']",
                      "*[style='display: none;']",      
                      "*[role='navigation']"
                      ,"*[aria-hidden='true']"]

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
    def main_content(soup):
        """Get main content from soup"""
        
        mains = soup.select("main") #get all main elements, tehre should only be one non hidden one
        mains_non_hidden = [m for m in mains if not "hidden" in m.attrs]
        if mains_non_hidden: # if there is a non hidden main element, use that
            main = mains_non_hidden[0] # get first non hidden main element
            if main: # if there is a viable main tag, remove all nav elements within it (if ny)
                s = HTMLCleaner.remove_all_nav(main, removables)
                return(" ".join(" ".join(t.strip().split()) \
                            for t in s.stripped_strings if t.strip() != ""))
        else:
            return ""

    @staticmethod
    def stripped(content, custom_removables=[]):
        removables.extend(custom_removables)
        soup = BeautifulSoup(content, 'lxml')
        HTMLCleaner.remove_all_nav(soup, removables)
        return(" ".join(" ".join(t.strip().split()) \
                        for t in soup.stripped_strings if t.strip() != ""))
    
    def clean_text(content, custom_removables=[]):
        """Get clean text from HTML content"""
        soup = BeautifulSoup(content, 'lxml')
        text = ""
        main = HTMLCleaner.main_content(soup) # get main content as specified by main tag
        print(f"Main text length: {len(main)}")
        if main: 
            text = main
        else:
            text = HTMLCleaner.stripped(content) # get stripped text, irrespective of main tag
            print(f"Stripped text length: {len(text)}")
        print(f"Clean text length in bytes: {len(text.encode('utf-8'))}")
        return text
        
        

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
    #url = "https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_9069952433271538175%22%7D&n_type=1&p_from=3"
    url = "https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/migration?tabs=python%2Cdalle-fix"
    html = requests.get(url).text
    
    print(f"HTML length: {len(html)}")
    
    soup = BeautifulSoup(html, 'lxml')
    main = HTMLCleaner.main_content(soup) # get main content as specified by main tag
    print(f"Main text length: {len(main)}")
    stripped = HTMLCleaner.stripped(html) # get stripped text, irrespective of main tag
    text  = ""
    
    if main:
        text = main
    else:
        text = stripped
    
    print(f"Stripped text length: {len(stripped)}")
    print(f"Clean text length: {len(text)}")
    print(f"Clean text length in bytes: {len(text.encode('utf-8'))}")
    with open("stripped.txt", "w", encoding='utf-8') as f:
        f.write(text)