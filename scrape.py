"""
Run command in terminal console eg: python scrape.py input.csv where input.csv 
has the first column named 'url' and each row beneath is a valid URL.
"""
import requests

import re
import csv
import sys

EMAIL_RE = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
CONTACT_US_RE = r"(?<=href=\")([^\"]*contact[-_]us[^\"]*)(?<!\")"


def search_for_emails(webpage_html: str, url: str) -> set[str]:
    emails_matched = re.finditer(EMAIL_RE, webpage_html)
    emails = {e.group(0) for e in emails_matched}
    print(f"Found {len(emails)} at {url}")
    if emails:
        print('\n'.join("  " + e for e in sorted(emails, key=lambda e: len(e))))
    return emails


def find_other_urls(webpage_html: str, base_url: str) -> set[str]:
    urls_matched = re.finditer(CONTACT_US_RE, webpage_html)
    urls = {base_url + u.group(1) for u in urls_matched}
    return urls


def scrape_emails(base_url: str) -> list[str]:
    if base_url[-1] == "/":
        base_url = base_url[:-1]

    webpage_html = requests.get(base_url).text
    emails = search_for_emails(webpage_html, base_url)
    other_urls = find_other_urls(webpage_html, base_url)

    for url in other_urls:
        other_webpage_html = requests.get(url).text
        more_emails = search_for_emails(other_webpage_html, url)
        emails.update(more_emails)
    
    print()
    return emails


if __name__ == "__main__":
    if len(sys.argv) == 2 and ".csv" in (filename := sys.argv[1]):
        with open(filename, "r") as file:
            for row in csv.DictReader(file):
                scrape_emails(row["url"])
    else:
        print(f"ERROR: Script requires input .csv as arg eg: 'python {sys.argv[0]} input.csv'")
        exit(1)
