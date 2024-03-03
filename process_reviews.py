import os
import pickle
import time
from pathlib import Path

import pandas
from progress.bar import IncrementalBar

from review_parser import parse_review as parse
from review_parser_old import parse_review as parse_old

DATA_PATH = Path("../data/")
REVIEWS_PATH = DATA_PATH / "reviews"
UNPROCESSED_PATH = REVIEWS_PATH / "unprocessed"
PROCESSED_PATH = REVIEWS_PATH / "processed"
MULTIALBUM_PATH = REVIEWS_PATH / "multi-album"
PROBLEM_PATH = REVIEWS_PATH / "problem_children"
DATAFRAME_PATH = DATA_PATH / "reviews_dataframe.p"
REVIEWS_JSON = DATA_PATH / "reviews.json"
LOG_PATH = "./log.txt"


def log(string, category, verbose=False):
    log_string = f"{time.strftime('%x %X', time.gmtime())} [{category}] {string}"
    with open(LOG_PATH, 'a+') as log:
        log.write(log_string)
        log.write("\n")
    if verbose:
        print(log_string)


def parse_review(filepath: Path):
    with filepath.open(encoding='utf-8') as f:
        text = f.read()
    name = filepath.name

    try:
        return parse_old(name, text)
    except NotImplementedError:
        log(f"Unable to deal with multi-album review {name}", "WARNING")
        filepath.rename(MULTIALBUM_PATH / name)
        return None
    except:
        try:
            return parse(name, text)
        except NotImplementedError:
            log(f"Unable to deal with multi-album review {name}", "WARNING")
            filepath.rename(MULTIALBUM_PATH / name)
        except Exception as err:
            log(f"Couldn't parse {name}", "WARNING")
            log(f"{err.__str__()}", "WARNING")
            filepath.rename(PROBLEM_PATH / name)
        return None


def iterate_reviews(move_files=False, compress_processed=False):
    MULTIALBUM_PATH.mkdir(exist_ok=True)
    PROBLEM_PATH.mkdir(exist_ok=True)

    num_unprocessed = len(os.listdir(UNPROCESSED_PATH))
    if num_unprocessed == 0:
        log("No reviews to process; exiting", "MESSAGE", True)
        exit(0)
        
    bar = IncrementalBar('Processing new reviews', max=num_unprocessed)
    data = []
    successes = 0
    failures = 0
    for f in UNPROCESSED_PATH.glob('*.txt'):
        parsed_review = parse_review(f)
        if parsed_review is not None:
            successes += 1
            data.append(parsed_review)
        else:
            failures += 1
        bar.next()
    bar.finish()
    log(f"Processing complete; {successes} successes and {failures} failures.", "MESSAGE", True)

    if successes == 0:
        exit(-1)

    df = None
    try:
        df: pandas.DataFrame = pickle.load(DATAFRAME_PATH.open('rb'))
        log(f"Successfully loaded dataframe; currently has {len(df.index)} rows", "MESSAGE", True)
    except IOError:
        log("Could not open pickled dataframe", "WARNING", True)

    new_df = pandas.DataFrame([r.to_dict() for r in data])
    if df is not None:
        if len(df.columns) != len(new_df.columns):
            log("Cannot concatenate old and new dataframes", "ERROR", True)
            exit(-1)
        df = pandas.concat([df, new_df], ignore_index=True)
    else:
        df = new_df
    df.to_pickle(DATAFRAME_PATH)
    log(f"Saved dataframe object; currently has {len(df.index)} rows", "MESSAGE", True)

    df.sort_values(by="score", inplace=True)
    df.to_json(REVIEWS_JSON, orient="records")
    log("Saved reviews JSON", "MESSAGE", True)

    if move_files:
        PROCESSED_PATH.mkdir(exist_ok=True)
        bar = IncrementalBar('Moving processed reviews', max=len(os.listdir(UNPROCESSED_PATH)))
        for filename in UNPROCESSED_PATH.glob('*.txt'):
            filename.rename(PROCESSED_PATH / filename.name)
            bar.next()
        bar.finish()

    if compress_processed:
        raise NotImplementedError

    exit(0)


if __name__ == "__main__":
    # print(parse_review("1-young-forever.txt")) # old format non-bnm
    # print(parse_review("the-roots-do-you-want-more.txt")) # old format bnm
    # print(parse_review("angelique-kidjo-mother-nature.txt")) # new format non-bnm
    # print(parse_review("yves-tumor-praise-a-lord-who-chews-but-which-does-not-consume-or-simply-hot-between-worlds.txt")) # new format bnm
    # print(parse_review("roc-marciano-the-alchemist-the-elephant-mans-bones.txt")) # new format multi-artist
    # print(parse_review("ghost-second-time-around-temple-stone-ghost.txt")) # multi-genre
    # print(parse_review("microstoria-init-ding-snd.txt")) # reissue
    # print(parse_review("jennifer-lopez-this-is-me-now.txt")) # multi-label

    iterate_reviews(move_files=True)
