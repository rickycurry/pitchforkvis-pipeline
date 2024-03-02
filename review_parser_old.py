import datetime
import html

import review

ARTIST = "artist-links artist-list single-album-tombstone__artist-links\">"
ALBUM_NAME = "single-album-tombstone__review-title\">"
ARTWORK = "single-album-tombstone__art\"><img src=\""
LABEL = "single-album-tombstone__meta-labels\">"
RELEASE_YEAR = "single-album-tombstone__meta-year\">"
SCORE = "score\">"
AUTHOR = "authors-detail__display-name\">"
AUTHOR_TITLE = "authors-detail__title\">"
GENRE = "genre-list genre-list--before\">"
PUBLISH_DATE = "pub-date\">"
ABSTRACT = "review-detail__abstract\">"
BODY = "review-detail__text clearfix\">"
BNM = "bnm-txt"


def simple_parse(text, delimiter, end, unescape=True):
    text = text.split(delimiter, 1)[-1]
    text_split = text.split(end, 1)
    ret = text_split[0]
    if unescape:
        ret = html.unescape(ret)
    text = text_split[1]
    return ret, text


def parse_review(filename, text):
    href = filename.split(".txt")[0]

    bnm = text.find(BNM) != -1

    artists = []
    artist_split = text.split(ARTIST)
    if len(artist_split) > 2:
        raise NotImplementedError("Multiple old-style ARTIST splits detected")
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

    text = text.split(ARTWORK)[-1]
    text_split = text.split('"', 1)
    artwork = text_split[0]
    artwork = html.unescape(artwork)
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
    abstract = text_split[0].replace('<p>', '').replace('</p>', '')
    abstract = html.unescape(abstract).strip()

    return review.Review(href,
                        artists,
                        album,
                        artwork,
                        labels,
                        year,
                        reissue_year,
                        score,
                        author,
                        author_title,
                        genres,
                        publish_date,
                        abstract,
                        bnm,
                        None)