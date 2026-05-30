import webbrowser
import urllib
from tavily import TavilyClient
from config.config import TAVILY_API_KEY

def search_ai(query):
    """
    Searches for a query using Tavily AI and returns the response.
    """
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.search(query)
        return response['results']
    except Exception as e:
        return {'error': f'Error in AI Search: {str(e)}'}

def search_google(query):
    """
    Searches for a query on Google and opens the search results in the default web browser.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return 'Google search completed successfully.'
    except Exception as e:
        return f'Error in Google Search: {str(e)}'


def search_youtube(query):
    """
    Searches for a query on YouTube and opens the search results in the default web browser.
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(url)
        return 'YouTube search completed successfully.'
    except Exception as e:
        return f'Error in YouTube Search: {str(e)}'


def handle_web_search(platform: str, query: str) -> bool | str | dict:
    platform = platform.lower().strip()
    if platform == 'ai':
        return search_ai(query)
    elif platform == 'google':
        return search_google(query)
    elif platform == 'youtube':
        return search_youtube(query)
    else:
        return f'Invalid web search platform: {platform}'