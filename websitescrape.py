import trafilatura

def scrape(url):
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded)
