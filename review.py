class Review(object):
    def __init__(self,
                 href,
                 artists,
                 album,
                 artwork,
                 labels,
                 release_year,
                 reissue_year,
                 score,
                 author,
                 author_title,
                 genres,
                 publish_date,
                 abstract,
                 bnm,
                 body_text):
        self.href = href
        self.artists = artists
        self.album = album
        self.artwork = artwork
        self.labels = labels
        self.release_year = release_year
        self.reissue_year = reissue_year
        self.score = score
        self.author = author
        self.author_title = author_title
        self.genres = genres
        self.publish_date = publish_date
        self.abstract = abstract
        self.bnm = bnm
        self.body_text = body_text

    def to_dict(self):
        return {
            "href": self.href,
            "artists": self.artists,
            "album": self.album,
            "artwork": self.artwork,
            "labels": self.labels,
            "release_year": self.release_year,
            "reissue_year": self.reissue_year,
            "score": self.score,
            "author": self.author,
            "author_title": self.author_title,
            "genres": self.genres,
            "publish_date": self.publish_date,
            "abstract": self.abstract,
            "bnm": self.bnm
        }

    def __str__(self):
        reissue_string = f"Reissue year: {self.reissue_year}\n" if self.reissue_year is not None else ""
        author_title_string = f"Author title: {self.author_title}\n" if self.author_title is not None else ""
        return (
            f"href: {self.href}\n"
            f"Artists: {self.artists}\n"
            f"Album: {self.album}\n"
            f"Artwork: {self.artwork}\n"
            f"Labels: {self.labels}\n"
            f"Release year: {self.release_year}\n"
            f"{reissue_string}"
            f"Score: {self.score}\n"
            f"Author: {self.author}\n"
            f"{author_title_string}"
            f"Genres: {self.genres}\n"
            f"Publish date: {self.publish_date}\n"
            f"Abstract: {self.abstract}\n"
            f"Best New Music: {self.bnm}\n"
        )
