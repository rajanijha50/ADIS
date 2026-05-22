import webbrowser
import urllib
from tavily import TavilyClient
from config.config import TAVILY_API_KEY

def search_ai(query):
    """
    Searches for a query on AI(tavily) and returns the response.
    """
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.search(query)
        return response['results']
    except Exception:
        return 'Error in AI Search'

def search_google(query):
    """
    Searches for a query on Google and opens the search results in the default web browser.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return 'Google search completed successfully.'
    except Exception:
        return 'Error in Google Search'


def search_youtube(query):
    """
    Searches for a query on YouTube and opens the search results in the default web browser.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return 'YouTube search completed successfully.'
    except Exception:
        return 'Error in YouTube Search'


def handle_web_search(mode: str, query: str):
    if mode == 'ai':
        return search_ai(query)
    elif mode == 'google':
        return search_google(query)
    elif mode == 'youtube':
        return search_youtube(query)
    else:
        return 'Invalid web search mode'