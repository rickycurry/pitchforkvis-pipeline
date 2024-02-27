import os
import time
import requests

BASE_PAGE_URL = "https://pitchfork.com/reviews/albums/?page="
BASE_REVIEW_URL = "https://pitchfork.com"
DELIMITER = 'class="review"><a href="'
LOG_PATH = "./log.txt"
NEWEST_FETCHED_PATH = "./newest_fetched.txt"
NEWEST_FETCHED_TEMP_PATH = "./newest_fetched_temp.txt"
REVIEW_DIRECTORY = "../data/reviews/"
LOCAL_REVIEWS = set(os.listdir(REVIEW_DIRECTORY))
SLEEP_TIME = 1 # second
RETRY_ATTEMPTS = 5
VERBOSE_LOGGING = True


def log(string, category):
    with open(LOG_PATH, 'a+') as log:
        log.write(f"{time.strftime('%x %X', time.gmtime())} [{category}] {string}\n")


def make_request(url):
    attempt = 1
    while attempt <= RETRY_ATTEMPTS:
        review = requests.get(url)
        status_string = f"URL {url} returned status {review.status_code}"
        if VERBOSE_LOGGING:
            print(status_string)

        time.sleep(SLEEP_TIME)

        if review.status_code == 200:
            return review.text
        
        elif review.status_code == 404:
            raise AttributeError("404, end of the line")
        
        log(f"{status_string} -- attempt #{attempt}", "WARNING")
        attempt += 1

    log(f"{status_string} -- no more retries left. Aborting", "ERROR")
    raise ConnectionError


def teardown(success):
    if success:
        os.remove(NEWEST_FETCHED_PATH)
        os.rename(NEWEST_FETCHED_TEMP_PATH, NEWEST_FETCHED_PATH)
        log("Teardown complete", "MESSAGE")
    else:
        os.remove(NEWEST_FETCHED_TEMP_PATH)
        log("Teardown complete but execution was not fully successful", "WARNING")


def get_pages():
    i = 1
    try:
        newest_fetched_file = open(NEWEST_FETCHED_PATH, 'r')
    except FileNotFoundError:
        newest_fetched_href = ""
    else:
        with newest_fetched_file:
            newest_fetched_href = newest_fetched_file.readline().strip()
            status_string = f"Previous newest fetched review is {newest_fetched_href}"
            print(status_string)
            log(status_string, "MESSAGE")

    keep_going = True
    while keep_going:
        url = BASE_PAGE_URL + str(i)
        try:
            page = make_request(url)
        except ConnectionError:
            break
        # I should make a custom exception for this
        # 404 means we've made it all the way to the end of Pitchfork
        except AttributeError: 
            teardown(True)
            exit()
        
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
            log("Successfully reached previous newest fetched review", "MESSAGE")
            teardown(True)
            exit()

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
    with open(f"{REVIEW_DIRECTORY}unprocessed/{album_name}.txt", 'w') as out:
    # with open(f"{REVIEW_DIRECTORY}{album_name}.txt", 'w') as out:
        out.write(review)
    return True


if __name__ == '__main__':
    get_pages()
