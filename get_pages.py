import os
import time

import requests

BASE_PAGE_URL = "https://pitchfork.com/reviews/albums/?page="


def get_pages(deleted=None):
    if deleted is None:
        deleted = []
    for i in deleted:
        url = BASE_PAGE_URL + str(i)
        r = requests.get(url)
        print(f"url {url} returned status {r.status_code}")
        if r.status_code != 200:
            break
        with open(f"./data/pages/page_{i}.txt", 'w') as out:
            out.write(r.text)
        time.sleep(2)


def get_deleted_pages():
    deleted = list(range(1, 1968))
    pages = os.listdir("./data/pages/")
    for fname in pages:
        number = int(fname.split('_')[1].split('.')[0])
        deleted.remove(number)
    print(f"missing pages: {deleted}")
    if len(deleted) != 0:
        get_pages(deleted)


if __name__ == '__main__':
    get_deleted_pages()

