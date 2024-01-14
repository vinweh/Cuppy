import textwrap
import requests
from htmlcleaner import HTMLCleaner

class TextSummarizer:
    """Class to summarize text using OpenAI API. 
    Not all that great yet, but it's a start. Very much a WIP
    
    Challenges: 
    - Creating a coherent summary over a text that requires summarizing multiple chunks.
    - Using textwrap for splitting text into chunks is not ideal, as there is no guarantee that sentences
    stay intact."""
    def __init__(self, useAzure=False
                ,model="gpt-3.5-turbo-0613", deployment_name="gpt35t-0613") -> None:
        
        self.useAzure = useAzure
        self.model = model
        self.deployment_name = deployment_name
        #get the right client if Azure true/false
        self.client = TextSummarizer.create_api_client(self.useAzure)
        
    
    @staticmethod
    def create_api_client(useAzure):
        if useAzure:
            from openai import AzureOpenAI
            return AzureOpenAI()
        else:
            from openai import OpenAI
            return OpenAI()

    def summarize(self, text, max_length=1000):
        # Split the text into chunks
        chunks = textwrap.wrap(text, max_length) 
        model = [self.model, self.deployment_name][self.useAzure]
        prompt = "Summarize the following text concisely in less than 200 words:\n\n"
        sys_message = {"role": "system", "content": prompt}
        messages = []
        messages.append(sys_message)
            
        summaries = []
        for chunk in chunks:
            # Use the OpenAI API to summarize the chunk
            messages.append({"role": "user", "content": chunk})
        
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=1000
                )

            # Add the summary to the list
            summaries.append(response.choices[0].message.content)
            messages = []

        return summaries
    
if __name__ == "__main__":
    # Example usage
    ts = TextSummarizer()
    text = requests.get("https://en.wikipedia.org/wiki/Bothell%2C_Washington").text
    print(f"Text length before cleaning: {len(text)}")
    text = HTMLCleaner.clean_text(text, custom_removables=['div.reflist', '.vector-dropdown-content'
                                                           ,'.vector-dropdown-label'
                                                           ,'.interlanguage-link'
                                                           ,'.interlanguage-link-target'
                                                           ,'span'
                                                           ,'.vector-dropdown-checkbox mw-interlanguage-selector'
                                                           , '.uls-lcd-region-section'
                                                           , '.row uls-language-list uls-lcd'
                                                           , '.grid uls-menu uls-medium'])
    summaries = ts.summarize(text)
    print(summaries)