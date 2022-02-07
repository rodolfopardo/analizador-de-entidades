import requests
import textrazor
from google.cloud import language_v1




class TextRazorAnalyzer:
    def __init__(self, api_key):
        """ Initializes TextRazorAnalyzer

        Args:
            api_key (str): The API key for TextRazor
        """
        textrazor.api_key = api_key
        self.client = textrazor.TextRazor(
            extractors=["entities", "topics"],
        )
        self.client.set_classifiers(["textrazor_mediatopics"])
        self.client.set_cleanup_return_cleaned(True)

    def analyze(self, text, is_url):
        """ Analyzes text with TextRazor

        Args:
            text (str): The text to analyze
            is_url (bool): Whether the text is a URL

        Returns:
            response (TextRazorResponse): The response from TextRazor
        """
        if is_url:
            response = self.client.analyze_url(text)
        else:
            response = self.client.analyze(text)
        return response


class GoogleNLPAnalyzer:
    def __init__(self, key):
        """ Initializes GoogleNLPAnalyzer

        Args:
            key (str): The API key for GoogleNLP
        """
        self.client = language_v1.LanguageServiceClient.from_service_account_info(key)

    def analyze(self, text, is_url):
        """ Analyzes text with GoogleNLP

        Args:
            text (str): The text to analyze
            is_url (bool): Whether the text is a URL

        Returns:
            response (GoogleNLPResponse): The response from GoogleNLP
        """
        if is_url:
            html = self.load_text_from_url(text)
            if not html:
                return None
            document = language_v1.Document(
                content=html, 
                type_=language_v1.Document.Type.HTML
            )
            response = self.client.analyze_entities(
                document=document
            )
        else:
            document = language_v1.Document(
                content=text, 
                type_=language_v1.Document.Type.PLAIN_TEXT
            )

            response = self.client.analyze_entities(
                document=document
            )
        return response
    

    def load_text_from_url(self, url):
        """ Loads text from a URL

        Args:
            url (str): The URL to load text from

        Returns:
            text (str): The text loaded from the URL
        """
        timeout = 20

        results = []

        try:
            
            headers = {'User-Agent': 'My User Agent 1.0'}
            # print("Extracting text from: {}".format(url))
            response = requests.get(url, headers=headers, timeout=timeout)

            text = response.text
            status = response.status_code

            if status == 200 and len(text) > 0:
                return text
            
            return None
        except Exception as e:
            print(e)
            print('Problem with url: {0}.'.format(url))
            return None
