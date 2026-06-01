import platform
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
        results = response.get('results') if isinstance(response, dict) else response
        # if results is not a list or empty, return raw response
        if not results or not isinstance(results, list):
            return {'error': 'No results from AI search.'}

        def _best_result_sentence(results_list):
            # pick item with highest score if present, else first item
            try:
                best = max(results_list, key=lambda x: x.get('score', 0))
            except Exception:
                best = results_list[0]

            # prefer content, fall back to title, then url
            text = best.get('content') or best.get('title') or best.get('url') or ''
            text = text.strip()
            if not text:
                return ''

            # extract first sentence (up to first period). Keep it concise.
            if '.' in text:
                sentence = text.split('.', 1)[0].strip()
                # if that was too short, maybe include next clause
                if len(sentence) < 20 and len(text) > len(sentence):
                    # take up to next period
                    parts = text.split('.')
                    sentence = '.'.join(p.strip() for p in parts[:2]).strip()
                return sentence + '.' if not sentence.endswith('.') else sentence
            # no period, return up to 200 chars
            return (text[:197].rstrip() + '...') if len(text) > 200 else text

        return _best_result_sentence(results)
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
    query = query.lower().strip()
    if not platform or not query:
        return "Error: Platform and Query must be provided"
    if platform == 'ai' or platform in ['ai','chatgpt','chatbot','gemini','claude']:
        return search_ai(query)
    elif platform == 'google':
        return search_google(query)
    elif platform == 'youtube':
        return search_youtube(query)
    else:
        return f'Invalid web search platform: {platform}'


# print(handle_web_search("ai", "Who is current president of USA?"))