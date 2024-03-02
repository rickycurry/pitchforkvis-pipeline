import datetime
import html

import review

BNM = "BestNewMusicText"
ABSTRACT = '<meta name="description" content="'
ARTWORK = "320w" #1, multiple
ALBUM_NAME = '"headline":"' #1505, multiple
ARTIST = 'SplitScreenContentHeaderArtist-ftloCc iUEiRd jqOMmZ kRtQWW">' #1520, multiple (as many as there are artists)
RELEASE_YEAR = 'class="SplitScreenContentHeaderReleaseYear-UjuHP huwRqr">' #1520, multiple
GENRE = 'Genre:</p><p class="BaseWrap-sc-gjQpdd BaseText-ewhhUZ InfoSliceValue-tfmqg iUEiRd dcTQYO fkSlPp">' #1520
LABEL = 'Label:</p><p class="BaseWrap-sc-gjQpdd BaseText-ewhhUZ InfoSliceValue-tfmqg iUEiRd dcTQYO fkSlPp">' #1520
PUBLISH_DATE = 'Reviewed:</p><p class="BaseWrap-sc-gjQpdd BaseText-ewhhUZ InfoSliceValue-tfmqg iUEiRd dcTQYO fkSlPp">' #1524, multiple
AUTHOR_TITLE = '"dangerousTitle":"' #1524, multiple
AUTHOR = '"name":"' #1524, multiple
SCORE = '"score":' #1524, multiple
BODY = ""
MULTIREVIEW = 'MultiReviewContentHeaderArtist'


def simple_parse(text, delimiter, end, unescape=True):
    text = text.split(delimiter, 1)[-1]
    text_split = text.split(end, 1)
    ret = text_split[0]
    if unescape:
        ret = html.unescape(ret)
    text = text_split[1]
    return ret, text


def parse_review(filename, text):
    if text.find(MULTIREVIEW) != -1:
        # TODO: figure out how to deal with multi-album reviews
        raise NotImplementedError('Unable to deal with multi-album review')

    href = filename.split(".txt")[0]

    bnm = text.find(BNM) != -1

    abstract, text = simple_parse(text, ABSTRACT, '"/>')

    text_split = text.split(ARTWORK, 1)
    text = text_split[-1]
    text_split = text_split[0].split(' ')
    artwork = text_split[-2]

    album, text = simple_parse(text, ALBUM_NAME, '"')

    artists = []
    artist_split = text.split(ARTIST)
    artist_split.pop(0) # throw out everything before split
    for split in artist_split:
        artists.append(split.split("<")[0])
    text = artist_split[-1]

    year, text = simple_parse(text, RELEASE_YEAR, '<')
    year = int(year)
    reissue_year = None

    genre, text = simple_parse(text, GENRE, '<')
    genres = genre.split(' / ')

    label, text = simple_parse(text, LABEL, '<')
    labels = label.split(' / ')

    date_string, text = simple_parse(text, PUBLISH_DATE, '<')
    publish_date = datetime.datetime.strptime(date_string, '%B %d, %Y')

    author_title, text = simple_parse(text, AUTHOR_TITLE, '"')

    author, text = simple_parse(text, AUTHOR, '"')

    score, text = simple_parse(text, SCORE, '}')
    score = float(score)

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