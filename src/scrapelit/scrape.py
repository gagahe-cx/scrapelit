"""
Written by: Yijia (Gaga) He
"""

import time
import requests
import lxml.html
from urllib.parse import urlparse


ALLOWED_DOMAINS = ("https://pubmed.ncbi.nlm.nih.gov/",)
REQUEST_DELAY = 1

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
)


def make_request(url):
    # This function follows CAPP122 PA2 taught by James Turk
    """
    Make a request to `url` and return the raw response.
    """
    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        raise ValueError(f"cannot fetch {url}, must be in {ALLOWED_DOMAINS}")

    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    response = session.get(url)
    response.raise_for_status()
    return response


def make_link_absolute(rel_url, current_url):
    # This function is taken from CAPP122 PA2 taught by James Turk
    """
    Given a relative URL like "/abc/def" or "?page=2"
    and a complete URL like "https://example.com/1/2/3" this function will
    combine the two yielding a URL like "https://example.com/abc/def"

    Parameters:
        * rel_url:      a URL or fragment
        * current_url:  a complete URL used to make the request that contained
        a link to rel_url

    Returns:
        A full URL with protocol & domain that refers to rel_url.
    """
    url = urlparse(current_url)
    if rel_url.startswith("/"):
        return f"{url.scheme}://{url.netloc}{rel_url}"
    elif rel_url.startswith("?"):
        return f"{url.scheme}://{url.netloc}{url.path}{rel_url}"
    else:
        return rel_url


def filter_url_with_words(keyword: list[str], start_year: str, end_year: str) -> str:
    """
    Constructs a PubMed search URL based on keywords and a date range.

    Args:
        keyword (list[str]): A list of keywords to include in the search.
        start_year (str): The start year for the search filter.
        end_year (str): The end year for the search filter.

    Returns:
        str: A PubMed search URL that includes the keywords and date range.

    Example use:
        keywords = ["Asthma", "social", "US"]
        start_year = "2023"
        end_year = "2024"
        search_url = filter_url_with_words(keywords, start_year, end_year)
        print(search_url)
    """
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    query = "+".join(keyword)
    filter_url = f"{base_url}?term={query}&filter=years.{start_year}-{end_year}"
    return filter_url


def get_next_page_url(url):
    """
    Determines and returns the URL of the next page of listings from the current
        webpage.

    Args:
        url (str): The URL of the current webpage from which the next page URL
        is to be found.

    Returns:
        str or None: The absolute URL of the next page if found, otherwise None.
    """
    response = make_request(url)
    root = lxml.html.fromstring(response.text)
    next_page_link = root.xpath(
        '//div[@class="search-results-chunk results-chunk"]/@data-next-page-url'
    )

    if next_page_link:
        next_page_url = make_link_absolute(next_page_link[0], url)
        return next_page_url
    else:
        return None


def get_each_paper(url):
    response = make_request(url)
    root = lxml.html.fromstring(response.text)
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    paper_queries = root.xpath('//a[@class="docsum-title"]/@href')
    paper_link = [f"{base_url}{paper_query}" for paper_query in paper_queries]
    return paper_link


def clean_text(text_list):
    """
    Cleans a list of text by stripping and joining.
    """
    return " ".join([text.strip() for text in text_list if text.strip()])


def crawl_each_paper(url):
    """
    Scrapes detailed information from a single doctor's profile page and returns
    it as a dictionary.

    Args:
        url (str): The URL of the doctor's profile page to scrape.

    Returns:
        dict: A dictionary containing various pieces of information scraped from
        the doctor's profile.
    """
    results = {}
    response = make_request(url)

    root = lxml.html.fromstring(response.content)

    queries = {
        "PubMed_ID": '//span[@class="id-label" and contains(text(), "PMID:")]/\
        following-sibling::strong[@class="current-id"]/text()',
        "Title": '//h1[@class="heading-title"]/text()',
        "Citation_Year": '//span[@class="citation-year"]//text()',
        "Authors": "//a[@class='full-name']/@data-ga-label",
        "Journal": "//button[@id='full-view-journal-trigger']/text()[1]",
        "Abstract": '//div[@class="abstract"]//text()',
    }

    for key, xpath in queries.items():
        query_result = root.xpath(xpath)
        if key == "Citation_Year" and query_result == "Null":
            query_result = root.xpath('//time[@class="citation-year"]//text()')
        if key == "Title" or key == "Abstract":
            results[key] = clean_text(query_result) if query_result else "Null"
        else:
            results[key] = query_result[0].strip() if query_result else "Null"

    return results


def crawl(keyword, start_year, end_year, limit):
    search_url = filter_url_with_words(keyword, start_year, end_year)
    count = 0
    result = []
    while count <= limit:
        count += 1
        paper_links = get_each_paper(search_url)
        for link in paper_links:
            result.append(crawl_each_paper(link))
        search_url = get_next_page_url(search_url)

    return result
