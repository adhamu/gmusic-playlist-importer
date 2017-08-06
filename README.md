# Gmusic Playlist Importer

## Introduction
This is a modified version of Simon Weber's playlist importer for Google Play Music (which can be found here: https://github.com/simon-weber/Google-Music-Playlist-Importer).

## Why Did I Modify It?
- I needed a different regex pattern as my music library is set up differently.
- I wanted to simplify the script so it had less manual intervention

## Requirements
- Python >= 2.7
- [My forked version of `gmusicapi`](https://github.com/adhamu/gmusicapi/tree/patch-2) which fixes a couple of bugs in `tools.py`. It's currently pointing to a `patch-2` branch. [Once my open PR to the main repository](https://github.com/simon-weber/gmusicapi/pull/567) gets approved/merged, this will no longer be necessary. Don't know why TravisCI is crying about it.

## Supports
I have only tested the script with M3U and M3U8 playlist formats.

## Usage

```python
python import.py my-playlist.m3u
```

## What It Does
- Goes through your playlist file and attempts to match each song with one in your Google Music library
- Creates a playlist automatically with the filename of the playlist (minus the file extension)
- The power of the `gmusicapi` asks you to choose a result if there's a "tie-break" (more than one match found)
- Adds all matched results to your new playlist

## What It Won't Do
- Check if the playlist exists. This means if you run the same import twice, it will create a duplicate. Google isn't that fussy about unique names for playlists.