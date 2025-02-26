# scrapelit

**Scrapelit** is a lightweight Python library for web scraping that simplifies extracting literatures from websites.

## Installation

Install Scrapelit using pip (requires Python 3.10+):

```bash
pip install scrapelit
```

*(If not yet on PyPI, you can install directly from GitHub: `pip install git+https://github.com/gagahe-cx/scrapelit.git`.)*

## Basic Usage

Scrapelit provides a simple API to fetch and parse web pages. Below are a couple of basic examples:

```python
from scrapelit import Scrapelit

scraper = Scrapelit()  
soup = scraper.fetch("https://example.com")            # Fetch page content (static HTML)
print(soup.title.text)                                 # Extract data (page title) using BeautifulSoup
```

```python
# Fetch a page that requires JavaScript (uses Selenium under the hood)
soup = scraper.fetch("https://example.com/dynamic-page", dynamic=True)
items = [item.text for item in soup.find_all("div", class_="listing")]  # Extract content by HTML element
print(items)
```

In the example above, `scraper.fetch()` returns a BeautifulSoup object (`soup`) for the requested page. You can then use familiar BeautifulSoup methods like `.find()` or `.find_all()` to locate the data you need. For pages that require JavaScript to load content, pass `dynamic=True` to let Scrapelit use Selenium to render the page before parsing.

---

Happy scraping!
