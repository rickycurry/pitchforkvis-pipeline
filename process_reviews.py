import datetime
import html
import os

import review
import pandas
import pickle


REVIEWS_PATH = "../data/reviews/"

ARTIST = "artist-links artist-list single-album-tombstone__artist-links\">"
ALBUM_NAME = "single-album-tombstone__review-title\">"
LABEL = "single-album-tombstone__meta-labels\">"
RELEASE_YEAR = "single-album-tombstone__meta-year\">"
SCORE = "score\">"
AUTHOR = "authors-detail__display-name\">"
AUTHOR_TITLE = "authors-detail__title\">"
GENRE = "genre-list genre-list--before\">"
PUBLISH_DATE = "pub-date\">"
ABSTRACT = "review-detail__abstract\">"
BODY = "review-detail__text clearfix\">"


def parse_review(filename):
    if filename == ".DS_Store":
        return
    with open(REVIEWS_PATH + filename, encoding='utf-8') as f:
        text = f.read()
    artists = []
    artist_split = text.split(ARTIST)
    if len(artist_split) > 2:
        return
    text = artist_split[1]
    text_split = text.split("</ul>", 1)
    artists_s = text_split[0]
    text = text_split[1]
    artists_s_list = artists_s.split("</li>")
    for s in artists_s_list:
        s = s.split("</a>")[0]
        artist = s.split(">")[-1]
        artist = html.unescape(artist)
        if len(artist) != 0:
            artists.append(artist)

    text = text.split(ALBUM_NAME)[-1]
    text_split = text.split("<", 1)
    album = text_split[0]
    album = html.unescape(album)
    text = text_split[1]

    labels = []
    text = text.split(LABEL, 1)[-1]
    text_split = text.split("</ul>", 1)
    labels_s = text_split[0]
    text = text_split[1]
    labels_s_list = labels_s.split("</li>")
    for s in labels_s_list:
        label = s.split(">")[-1]
        label = html.unescape(label)
        if len(label) != 0:
            labels.append(label)

    text = text.split(RELEASE_YEAR, 1)[-1]
    text_split = text.split("</span>", 1)
    year_s = text_split[0]
    text = text_split[1]
    year_s = year_s.split(">")[-1]
    year_s_split = year_s.split("/")
    year = None
    try:
        year = int(year_s_split[0])
    except ValueError:
        pass
    reissue_year = None
    if len(year_s_split) > 1:
        reissue_year = int(year_s_split[1])

    text = text.split(SCORE, 1)[-1]
    text_split = text.split("<", 1)
    score = float(text_split[0])
    text = text_split[1]

    text = text.split(AUTHOR, 1)[-1]
    text_split = text.split("<", 1)
    author = text_split[0]
    author = html.unescape(author)
    text = text_split[1]

    text_split = text.split(AUTHOR_TITLE, 1)
    text = text_split[-1]
    author_title = None
    if len(text_split) > 1:
        text_split = text.split("<", 1)
        author_title = text_split[0]
        text = text_split[1]

    genres = []
    text = text.split(GENRE, 1)[-1]
    text_split = text.split("</ul>", 1)
    genres_s = text_split[0]
    text = text_split[1]
    genres_s_list = genres_s.split("</li>")
    for s in genres_s_list:
        s = s.split("</a>")[0]
        genre = s.split(">")[-1]
        genre = html.unescape(genre)
        if len(genre) != 0:
            genres.append(genre)

    text = text.split(PUBLISH_DATE, 1)[-1]
    text = text.split(">", 1)[-1]
    text_split = text.split("<", 1)
    date_string = text_split[0]
    publish_date = datetime.datetime.strptime(date_string, '%B %d %Y')
    text = text_split[1]

    text = text.split(ABSTRACT, 1)[-1]
    text_split = text.split("</div>", 1)
    abstract = text_split[0]
    abstract = html.unescape(abstract)
    # text = text_split[1]

    review_obj = review.Review(artists,
                               album,
                               labels,
                               year,
                               reissue_year,
                               score,
                               author,
                               author_title,
                               genres,
                               publish_date,
                               abstract,
                               None)
    return review_obj


def iterate_reviews():
    try:
        df = pickle.load(open("../data/reviews_dataframe.p", 'rb'))
    except IOError:
        data = []
        for f in os.listdir(REVIEWS_PATH):
            parsed_review = parse_review(f)
            if parsed_review is not None:
                data.append(parsed_review)
        print(len(data))

        df = pandas.DataFrame([r.to_dict() for r in data])
        pickle.dump(df, open("../data/reviews_dataframe.p", 'wb'))

    df.sort_values(by="score", inplace=True)

    df.to_json("../data/reviews.json", orient="records")


if __name__ == "__main__":
    # parse_review("1-young-forever.txt")
    iterate_reviews()
