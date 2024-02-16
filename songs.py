from enum import Enum
import json
from fuzzywuzzy import fuzz


class Attributes(Enum):
    SMILE = 1
    PURE = 2
    COOL = 3


class Song:
    def __init__(self, id: int, title, group, attrib=Attributes(1)):
        self.id = id
        self.title = title
        self.group = group
        self.attribute = attrib
        self.difficulties = []

    def __str__(self):
        s = ""
        s += "ID: %d\n" % self.id
        s += "Song: %s\n" % self.title
        s += "Group: %s\n" % self.group.name
        s += "Attribute: %s\n" % self.attribute.name
        s += "Difficulties:\n"
        for i in self.difficulties:
            s += "      %s\n" % i
        return s

    def add_difficulty(self, diff, level, maxcombo=0):
        self.difficulties.append(Difficulty(diff, level, maxcombo))


class Songbook:
    def __init__(self):
        self.songs = []

    def add_song(self, song: Song):
        search = search_songs(song.title, self)
        if search is None:
            self.songs.append(song)
        else:
            print("Song was already found in database.")
            quit()

    def get_songs(self):
        return self.songs


class Difficulty:
    def __init__(self, diff, level, maxcombo=0):
        self.difficulty = Difficulties(diff)
        self.level = level
        self.maxcombo = maxcombo

    def __str__(self):
        s = ""
        s += "%s" % self.difficulty.name
        s += ": "
        s += "%d" % self.level
        # s += " %d" % self.maxcombo
        return s

    def set_maxcombo(self, combo):
        self.maxcombo = combo


def search_songs(title, songbook, threshold=60):
    best_match = (0, None)
    print(f"Searching for song {title}.")
    for song in songbook.songs:
        if song.title == title:
            print(f"Song found. {song.title}")
            return song
        similarity = fuzz.ratio(title, song.title)
        if similarity >= threshold:
            if similarity > best_match[0]:
                print(f"New best match found: {song.title} with {similarity}")
                best_match = (similarity, song)
    return best_match[1]


def search_songs_id(id: int, songbook):
    for song in songbook.songs:
        if song.id == id:
            return song
    return None


def save_songs(songs, filename='songs.json'):
    song_data = []
    for song in songs:
        song_entry = {
            'id': song.id,
            'title': song.title,
            'group': song.group.name,
            'attribute': song.attribute.name,
            'difficulties': [
                {
                    'difficulty': difficulty.difficulty.name,
                    'level': difficulty.level,
                    'maxcombo': difficulty.maxcombo
                }
                for difficulty in song.difficulties
            ]
        }
        song_data.append(song_entry)

    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump({'songs': song_data}, json_file, indent=2)


def load_songs(filename='songs.json'):
    songs = []

    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        song_entries = data.get('songs', [])

        for song_entry in song_entries:
            id = song_entry.get('id', 0)
            title = song_entry.get('title', '')
            group = song_entry.get('group', '')
            attribute = song_entry.get('attribute', '')
            difficulties = song_entry.get('difficulties', [])

            song = Song(id, title, Groups[group.upper()], Attributes[attribute.upper()])

            for difficulty_info in difficulties:
                difficulty = difficulty_info.get('difficulty', '')
                level = difficulty_info.get('level', 1)
                maxcombo = difficulty_info.get('maxcombo', 0)
                song.add_difficulty(Difficulties[difficulty.upper()], level, maxcombo)

            songs.append(song)

    return songs


class Difficulties(Enum):
    NORMAL = 1
    HARD = 2
    EXPERT = 3
    MASTER = 4


class Groups(Enum):
    MUSE = 1
    AQOURS = 2
    NIJIGAKU = 3
    LIELLA = 4
    HASUNOSORA = 5
    OTHER = 6
    PARHELION = 7
