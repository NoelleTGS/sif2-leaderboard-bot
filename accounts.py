import json
import math
import songs


class Score:
    def __init__(self, song: songs.Song, diff, perfect=0, great=0, good=0, bad=0, miss=0, combo=0):
        self.song = song
        self.difficulty = song.difficulties[diff]

        if (perfect + great + good + bad + miss) != self.difficulty.maxcombo:
            raise Exception(f"Score attributes do not match max combo.\n"
                            f"{self.song.title} [{self.difficulty.difficulty.name}]. "
                            f"Expected {self.difficulty.maxcombo}, got {perfect + great + good + bad + miss}.\n"
                            f"Either the wrong song was detected, or your score values weren't detected correctly.\n"
                            f"Please report in <#1203869549875699762> with your screenshot.")

        self.perfect = perfect
        self.great = great
        self.good = good
        self.bad = bad
        self.miss = miss
        self.combo = combo

        rawacc = (300 * self.perfect) + (200 * self.great) + (100 * self.good) + (50 * self.bad)
        self.accuracy = 100 * (rawacc / (300 * self.difficulty.maxcombo))

        self.performance = 10 * (self.difficulty.level * math.pow(self.accuracy / 98, 6))

    def __str__(self):
        s = ""
        s += "%s [%s] %2.2f%% %dp\n" % (
            self.song.title, self.difficulty.difficulty.name, self.accuracy, self.performance)

        return s


class Account:
    def __init__(self, name, id, friendcode=0):
        self.id = id
        self.name = name
        self.performance = 0
        self.accuracy = 100
        self.friendcode = friendcode
        self.scores = []

    def __str__(self):
        s = ""
        s += "%s\n" % self.name
        s += "Friend code: %d\n" % self.friendcode
        s += "Performance: %d\n" % self.performance
        s += "Average accuracy: %2.2f%%\n" % self.accuracy
        s += "Top plays:\n"
        for i in self.scores:
            s += "      %s" % i

        return s

    def create_score(self, song, diff, perfect=0, great=0, good=0, bad=0, miss=0, combo=0):
        score = Score(song, diff, perfect, great, good, bad, miss, combo)
        self.scores.append(score)
        self.scores.sort(key=lambda x: x.performance, reverse=True)
        self.calc_stats()

    def add_score(self, score: Score):
        for i in self.scores:
            if i.song.title == score.song.title:
                if i.difficulty == score.difficulty:
                    if i.performance >= score.performance:
                        return 0
                    else:
                        self.scores.remove(i)
        self.scores.append(score)
        self.scores.sort(key=lambda x: x.performance, reverse=True)
        self.calc_stats()
        return 1

    def set_friend_code(self, code):
        self.friendcode = code

    def calc_stats(self):
        self.performance = 0
        self.accuracy = 0
        weighting = 0

        for i, score in enumerate(self.scores):
            self.performance += score.performance * math.pow(0.95, i)
            self.accuracy += score.accuracy * math.pow(0.95, i)
            weighting += math.pow(0.95, i)

        self.accuracy = (self.accuracy / weighting)


def save_accounts(accounts, filename='accounts.json'):
    account_data = []
    for account in accounts:
        account_entry = {
            'id': account.id,
            'name': account.name,
            'friendcode': account.friendcode,
            'performance': account.performance,
            'accuracy': account.accuracy,
            'scores': [
                {
                    'song_title': score.song.title,
                    'difficulty': score.difficulty.difficulty.value - 1,
                    'perfect': score.perfect,
                    'great': score.great,
                    'good': score.good,
                    'bad': score.bad,
                    'miss': score.miss,
                    'combo': score.combo
                }
                for score in account.scores
            ]
        }
        account_data.append(account_entry)

    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump({'accounts': account_data}, json_file, indent=2)


def load_accounts(songbook, filename='accounts.json'):
    accounts = []

    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        account_entries = data.get('accounts', [])

        for account_entry in account_entries:
            id = account_entry.get('id', 0)
            name = account_entry.get('name', '')
            friendcode = account_entry.get('friendcode', 0)
            performance = account_entry.get('performance', 0)
            accuracy = account_entry.get('accuracy', 100)
            scores = account_entry.get('scores', [])

            account = Account(name, id, friendcode)
            account.performance = performance
            account.accuracy = accuracy

            for score in scores:
                song = score.get('song_title', '')
                difficulty = score.get('difficulty', 0)
                perfect = score.get('perfect', 0)
                great = score.get('great', 0)
                good = score.get('good', 0)
                bad = score.get('bad', 0)
                miss = score.get('miss', 0)
                combo = score.get('combo', 0)

                song = songs.search_songs(song, songbook)
                account.create_score(song, difficulty, perfect, great, good, bad, miss, combo)

            accounts.append(account)

    return accounts
