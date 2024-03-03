import pickle
import pandas
import numpy as np
import time
from collections import defaultdict
from pathlib import Path


DATA_PATH = Path("../data/")
LABELS_JSON = DATA_PATH / "labels.json"
DATAFRAME_PATH = DATA_PATH / "reviews_dataframe.p"
LOG_PATH = "./log.txt"


def log(string, category, verbose=False):
    log_string = f"{time.strftime('%x %X', time.gmtime())} [{category}] {string}"
    with open(LOG_PATH, 'a+') as log:
        log.write(log_string)
        log.write("\n")
    if verbose:
        print(log_string)

#  we want the resulting data to look like
#  [
#    {
#      "label": "Brainfeeder",
#      "mean": 7.5,
#      "median": 7.3,
#      "std_dev": 2.2,
#      "count": 19
#    },
#    ...
#  ]


class LabelData:
    def __init__(self):
        #  a flat list of scores
        self.scores = []
        #  a dictionary of genre counts
        self.genres = defaultdict(int)

    def majority_genre(self):
        threshold = 0.5
        review_count = len(self.scores)
        for genre_name, genre_count in self.genres.items():
            if genre_count / review_count > threshold:
                return genre_name
        return "Mixed"

    def to_dict(self, name):
        return {
            "label": name,
            "count": len(self.scores),
            "mean": np.mean(self.scores),
            "median": np.median(self.scores),
            "std_dev": np.std(self.scores),
            "majority_genre": self.majority_genre()
        }


def process_labels():
    #  load the dataframe
    df: pandas.DataFrame = pickle.load(DATAFRAME_PATH.open('rb'))

    labels_data = defaultdict(LabelData)

    for index, review in df.iterrows():
        review_labels = set(review['labels'])
        score = review['score']
        genres = review['genres']
        for label in review_labels:
            labels_data[label].scores.append(score)
            for genre in genres:
                labels_data[label].genres[genre] += 1

    processed_labels = []
    for name, data in labels_data.items():
        processed_labels.append(data.to_dict(name))

    processed_labels.sort(key=lambda d: d["count"])
    label_frame = pandas.DataFrame(processed_labels)
    # TODO: we probably don't have to make a new dataframe every time we run this
    label_frame.to_json(LABELS_JSON, orient="records")
    log("Saved labels JSON", "MESSAGE", True)


if __name__ == "__main__":
    process_labels()
