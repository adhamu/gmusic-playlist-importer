#!/usr/bin/env python

"""
This is a modified version of Simon Weber's playlist importer.

https://github.com/simon-weber/Google-Music-Playlist-Importer
Also using a modified version of tools.py from the gmusic api
whilst waiting for a pull request to be approved.
https://github.com/simon-weber/gmusicapi/pull/566
"""

import re
import sys
import os
import codecs
import credentials
import chardet
import gmusicapitools
from gmusicapi import Mobileclient

username = credentials.login['username']
password = credentials.login['password']

reload(sys)
sys.setdefaultencoding('utf8')


def init(max_attempts=3):
    """
    Make an instance of the api and attempts to login with it.

    Returns the api after at most max_attempts.
    :param max_attempts:
    """
    api = Mobileclient()

    logged_in = False
    attempts = 0

    print("Log in to Google Music.")

    while not logged_in and attempts < max_attempts:
        logged_in = api.login(username, password, Mobileclient.FROM_MAC_ADDRESS)
        attempts += 1

    return api


def guess_encoding(filename):
    """
    Return a tuple of (guessed encoding, confidence).

    :param filename:
    """
    res = chardet.detect(open(filename).read())
    return (res['encoding'], res['confidence'])


def main():
    """Main worker function."""
    if not len(sys.argv) == 2:
        print "usage:", sys.argv[0], "<playlist file>"
        sys.exit(0)

    # The three md_ lists define the format of the playlist and how matching should be done against the library.
    # They must all have the same number of elements.

    # Where this pattern matches, a query will be formed from the captures.
    # My example matches against a playlist file with lines like:
    # /home/simon/music/library/The Cat Empire/Live on Earth/The Car Song.mp3
    # Make sure it won't match lines that don't contain song info!
    md_pattern = ur"/Volumes/Macintosh HD 2/Amit/iTunes/(.*)/(.*)/(?:\d\d\s)?(.*)\..*$"

    # Identify what metadata each capture represents.
    # These need to be valid fields in the GM json - see protocol_info in the api repo.
    md_cap_types = ('artist', 'album', 'title')

    # The lower-better priority of the capture types above.
    # In this example, I order title first, then artist, then album.
    md_cap_pr = (2, 3, 1)

    # Build queries from the playlist.
    playlist_fname = sys.argv[1]
    playlist_name_for_google = os.path.splitext(os.path.basename(playlist_fname))[0]
    pl_encoding, confidence = guess_encoding(playlist_fname)

    queries = None
    with codecs.open(playlist_fname, encoding='utf-8', mode='r') as f:
        queries = gmusicapitools.build_queries_from(f,
                                     re.compile(md_pattern, re.UNICODE),
                                     md_cap_types,
                                     md_cap_pr,
                                     pl_encoding)

    api = init()
    if not api.is_authenticated():
        print "Failed to log in."
        sys.exit(0)

    print "Loading library from Google Music..."
    library = api.get_all_songs()

    print "Matching songs..."

    matcher = gmusicapitools.SongMatcher(library)

    matched_songs = matcher.match(queries)


    print matcher.build_log()

    p_id = api.create_playlist(playlist_name_for_google)

    print "Made playlist", playlist_name_for_google


    res = api.add_songs_to_playlist(p_id,
                            map(gmusicapitools.filter_song_md, matched_songs))
    print "Added songs."

if __name__ == '__main__':
    main()

