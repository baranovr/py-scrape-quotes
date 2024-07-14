import csv
import re
import time
import requests

from dataclasses import dataclass

from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


page = requests.get(BASE_URL).content
soup = BeautifulSoup(page, "html.parser")


def parse_one_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = [tag.text for tag in quote_soup.select("a.tag")]

    return Quote(
        text=quote_soup.select_one(".text").text.strip(),
        author=quote_soup.select_one(".author").text.strip(),
        tags=tags,
    )


def get_pages_count(page_soup: BeautifulSoup) -> int:
    pager = page_soup.select_one(".pager")

    if pager:
        page_links = pager.find_all("a", href=True)
        page_numbers = []

        for link in page_links:
            page_link = link["href"]
            match = re.search(r"/page/(\d+)/", page_link)

            if match:
                page_numbers.append(int(match.group(1)))

        if page_numbers:
            return max(page_numbers)

    return 1


def parse_quotes() -> list[Quote]:
    num = 1
    quotes = []

    pages_count = get_pages_count(soup)

    for page_num in range(1, pages_count + 1):
        one_page = requests.get(f"{BASE_URL}page/{page_num}/").content
        page_soup = BeautifulSoup(one_page, "html.parser")
        quote_soups = page_soup.select(".quote")

        for quote_soup in quote_soups:
            quotes.append(parse_one_quote(quote_soup))
            print(f"Parsing quote {num}...")
            num += 1

    print("\nParsing pages finished.\n")
    return quotes


def write_quotes_to_file(quotes: list[Quote], output_csv_path: str) -> None:
    num = 1

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])
            print(f"Writing the parsed quote {num}...")
            num += 1

    print("\nWriting the parsed quotes to .csv finished.")


def main() -> None:
    print("=== Parsing Quotes ===")
    print("Parsing quotes...\n")
    quotes = parse_quotes()

    print(
        "-------------------------------------\n"
        "Writing parsed quotes to .csv file...\n"
    )
    write_quotes_to_file(quotes, "quotes.csv")


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(f"\nSpent time: {end - start}")
