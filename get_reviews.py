import time
import os

import requests

BASE_PAGE_URL = "https://pitchfork.com"
DELIMITER = 'class="review"><a href="'
PAGES_DIRECTORY = "./data/pages/"


def iterate_pages():
    for f in os.listdir(PAGES_DIRECTORY):
        if f == "completed":
            continue
        success = get_reviews(f)
        if not success:
            break


# f is a filename
def get_reviews(f):
    with open(PAGES_DIRECTORY + f, 'r') as readfile:
        page = readfile.read()
    page_split = page.split(DELIMITER)
    for line in page_split:
        if line[0] == '/':
            href = line.split('"')[0]
            success = False
            while not success:
                time.sleep(2)
                success = get_review(href)
    # delete the page
    os.replace(PAGES_DIRECTORY + f, PAGES_DIRECTORY + "completed/" + f)
    return True


def get_review(href):
    url = BASE_PAGE_URL + href
    r = requests.get(url)
    print(f"url {url} returned status {r.status_code}")
    if r.status_code != 200:
        return False
    album_name = href.split('/')[-2]
    print(f"saving as {album_name}.txt")
    with open(f"./data/reviews/{album_name}.txt", 'w') as out:
        out.write(r.text)
    return True


if __name__ == '__main__':
    iterate_pages()
