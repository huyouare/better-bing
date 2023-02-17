import os
import requests
from urllib.parse import urlparse
from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Given a webpage, gets the list of links from this webpage (that link to the same website),
then crawls each one, extracts the text, and saves the text to a text file.
Only uses 1 level of recursion."""


class Crawler:
    """
    url - internet url
    output_folder - folder name to store data
    number_of_pages - limit on number of pages to download
    """

    def __init__(self, url, output_folder="unnamed", number_of_pages=1000):
        self.url = url
        if output_folder == "unnamed":
            output_folder = urlparse(url).netloc.replace(".", "-")
        self.output_folder = output_folder
        self.number_of_pages = number_of_pages

        # Creates a folder to store files
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    """Crawls the specificed website"""

    def crawl(self):
        print("Crawling " + self.url)
        url_list = self.extract_links(self.url)

        # Crawl each link, and write to file.
        # For performance, crawls only the first number_of_pages links
        for url in url_list[:self.number_of_pages]:
            self.save_page(url)

    """Save this page to a new file in output_folder"""

    def save_page(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_text = soup.get_text().strip()

        # Use URL path suffix to create filename. Strip leading "/".
        # Example: "http://www.paulgraham.com/talk.html" ->  "/talk.html" -> "talk.html"
        url_path = urlparse(url).path[1:]

        # Convert any extra "/" to "-".
        url_path = url_path.replace("/", "-")

        # Replace suffix with .txt
        # Example: "talk.html" -> "talk.txt"
        filename = os.path.splitext(url_path)[0] + ".txt"
        file_path = os.path.join(self.output_folder, filename)

        # Create the folder for this crawl if it does not exist.
        if not os.path.exists(os.path.dirname(filename)):
            os.mkdir(file_path)

        # Create and write filename
        with open(file_path, "w") as file:
            file.write(extracted_text)
            print("Created " + file_path)

    """
    Given the URL, returns a list of all links. Only include internal-links to this website.
    De-duplicate links so data is not downloaded multiple times.
    A self-link is added, so this page will always return at least 1 link.
    """

    def extract_links(self, url):
        parsed_url = urlparse(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all links on this page. Include a self-link
        all_links = [link.get('href') for link in soup.find_all('a')]
        all_links.append(url)

        # Filter known bad links
        def is_bad_link(link):
            parsed_link = urlparse(link)
            # Remove external links, i.e. links to another website. This also clears empty links.
            if parsed_link.netloc != "" and parsed_url.netloc != parsed_link.netloc:
                return True
            # Remove all Anchors (Ex: #Contents)
            if not parsed_link.path:
                return True
            # Otherwise, return OK for now.
            return False
        all_links = [link for link in all_links if not is_bad_link(link)]

        # Convert links of the format ['index.html', 'wisdom.html', etc] to full links
        full_links = []
        for link in all_links:
            if link.startswith("http://") or link.startswith("https://"):
                full_links.append(link)
            else:
                full_links.append(urljoin(url, link))

        # Only look at internal links, i.e. links to this website
        # This line converts https://www.crummy.com/software/BeautifulSoup/bs4/doc/ -> www.crummy.com
        domain = urlparse(url).netloc
        all_internal_links = [link for link in full_links if domain in link]

        # remove dupes
        res = sorted(set(all_internal_links))
        return res

    """Extract the domain name from a URL"""

    def get_domain(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc


def main():
    DATA_FOLDER_NAME = "data"
    URL = "http://www.paulgraham.com/articles.html"
    # URL = "https://pmarchive.com/"
    c = Crawler(URL, "data")
    c.crawl()


if __name__ == "__main__":
    main()
