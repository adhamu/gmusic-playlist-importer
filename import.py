#!/usr/bin/env python

"""
This is a modified version of Simon Weber's playlist importer.

https://github.com/simon-weber/Google-Music-Playlist-Importer
"""

import re
import sys
import os
import codecs
import credentials
import chardet
import gmusicapi.gmtools.tools as gmusicapitools
from gmusicapi import Mobileclient

username = credentials.login['username']
password = credentials.login['password']

reload(sys)
sys.setdefaultencoding('utf8')


def init(max_attempts=3):
    """Make an instance of the api and attempts to login with it."""
    api = Mobileclient()

    logged_in = False
    attempts = 0

    print('Log in to Google Music.')
    while not logged_in and attempts < max_attempts:
        logged_in = api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)
        attempts += 1

    return api


def guess_encoding(filename):
    """Return a tuple of (guessed encoding, confidence)."""
    res = chardet.detect(open(filename).read())
    return (res['encoding'], res['confidence'])


def main():
    """Main worker function."""
    if not len(sys.argv) == 2:
        print('usage:', sys.argv[0], '<playlist file>')
        sys.exit(0)

    playlist_filename = sys.argv[1]
    playlist_title = os.path.splitext(os.path.basename(playlist_filename))[0]
    playlist_encoding, confidence = guess_encoding(playlist_filename)

    queries = None
    with codecs.open(playlist_filename, encoding='utf-8', mode='r') as f:
        queries = gmusicapitools.build_queries_from(
            f,
            re.compile(
                ur"/Volumes/Macintosh HD 2/Amit/iTunes/(.*)/(.*)/(?:\d\d\s)?(.*)\..*$",
                re.UNICODE
            ),
            ('artist', 'album', 'title'),
            (2, 3, 1),
            playlist_encoding
        )

    api = init()
    if not api.is_authenticated():
        print('Failed to log in.')
        sys.exit(0)

    print('Loading library from Google Music...')
    library = api.get_all_songs()

    print('Matching songs...')
    matcher = gmusicapitools.SongMatcher(library)
    matched_songs = matcher.match(queries)

    print(matcher.build_log())
    p_id = api.create_playlist(playlist_title)
    print('Created playlist: ' + playlist_title)

    result = api.add_songs_to_playlist(
        p_id,
        map(gmusicapitools.filter_song_md, matched_songs)
    )
    print('Added ' + str(len(result)) + ' songs')

if __name__ == '__main__':
    main()
