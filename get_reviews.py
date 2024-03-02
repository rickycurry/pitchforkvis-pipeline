import os
import time
import requests
from pathlib import Path

BASE_PAGE_URL = "https://pitchfork.com/reviews/albums/?page="
BASE_REVIEW_URL = "https://pitchfork.com"
DELIMITER = 'class="review"><a href="'
LOG_PATH = "./log.txt"
NEWEST_FETCHED_PATH = "./newest_fetched.txt"
NEWEST_FETCHED_TEMP_PATH = "./newest_fetched_temp.txt"
REVIEW_DIRECTORY = Path("../data/reviews/unprocessed")
LOCAL_REVIEWS = set(os.listdir(REVIEW_DIRECTORY))
SLEEP_TIME = 1 # second
RETRY_ATTEMPTS = 5
VERBOSE_LOGGING = True


def log(string, category, verbose=False):
    log_string = f"{time.strftime('%x %X', time.gmtime())} [{category}] {string}"
    with open(LOG_PATH, 'a+') as log:
        log.write(log_string)
        log.write("\n")
    if verbose:
        print(log_string)


def make_request(url):
    attempt = 1
    while attempt <= RETRY_ATTEMPTS:
        r = requests.get(url)
        status_string = f"URL {url} returned status {r.status_code}"
        if VERBOSE_LOGGING:
            print(status_string)

        time.sleep(SLEEP_TIME)

        if r.status_code == 200:
            return r.text
        
        elif r.status_code == 404:
            teardown(True)
        
        log(f"{status_string} -- attempt #{attempt}", "WARNING")
        attempt += 1

    log(f"{status_string} -- no more retries left. Aborting", "ERROR")
    raise ConnectionError


def teardown(success):
    if success:
        os.remove(NEWEST_FETCHED_PATH)
        os.rename(NEWEST_FETCHED_TEMP_PATH, NEWEST_FETCHED_PATH)
        log("Teardown complete", "MESSAGE", True)
        exit(0)
    else:
        os.remove(NEWEST_FETCHED_TEMP_PATH)
        log("Teardown complete but execution was not fully successful", "WARNING", True)
        exit(-1)


def get_pages():
    i = 1
    REVIEW_DIRECTORY.mkdir(exist_ok=True)
    try:
        newest_fetched_file = open(NEWEST_FETCHED_PATH, 'r')
    except FileNotFoundError:
        newest_fetched_href = ""
    else:
        with newest_fetched_file:
            newest_fetched_href = newest_fetched_file.readline().strip()
            log(f"Previous newest fetched review is {newest_fetched_href}", "MESSAGE", True)

    keep_going = True
    while keep_going:
        url = BASE_PAGE_URL + str(i)
        try:
            page = make_request(url)
        except ConnectionError:
            break
        
        keep_going = get_reviews(page, newest_fetched_href)
        i += 1

    teardown(False)


def get_reviews(page, newest_fetched_href):
    page_split = page.split(DELIMITER)
    for line in page_split:
        if line[0] != '/':
            continue
        href = line.split('"')[0]

        # Keep track of the newest review href we fetched
        if not os.path.isfile(NEWEST_FETCHED_TEMP_PATH):
            with open(NEWEST_FETCHED_TEMP_PATH, 'w') as temp:
                temp.write(href)

        # Check to see if we reached our target destination yet
        if href == newest_fetched_href:
            log("Successfully reached previous newest fetched review", "MESSAGE", True)
            teardown(True)

        # Check if we already have the review
        album_name = href.split('/')[-2]
        review_name = album_name + ".txt"
        if review_name in LOCAL_REVIEWS:
            print(f"Skipping {review_name} that we already have")
            continue

        if not get_review(href, album_name):
            return False

    return True


def get_review(href, album_name):
    url = BASE_REVIEW_URL + href
    try:
        review = make_request(url)
    except ConnectionError:
        return False

    print(f"Saving as {album_name}.txt")
    f_path = REVIEW_DIRECTORY / f"{album_name}.txt"
    with f_path.open(mode='w') as out:
        out.write(review)
    return True


if __name__ == '__main__':
    get_pages()
