import re
from urllib.request import urlopen
import songs
import html as htmlprocess
import accounts

url = "https://love-live.fandom.com/wiki/Love_Live!_School_idol_festival"
page = urlopen(url)
html_bytes = page.read()
html = html_bytes.decode("utf-8")

htmltexts = ["µ's Mode Songs", "Aqours Mode Songs", "Nijigasaki High School Idol Club Mode Songs", "Liella! Mode Songs",
             "id=\"Events_2\""]
html_pattern = r'<tr>(.*?)</tr>'
title_pattern = r'<a\s+href="/wiki/[^"]+"\s+title="([^"]+)">'
number_pattern = r'<td style="text-align:center;">(\d+)'
attribute_pattern = r'<img alt="SIF (\w+) Icon"'



# for k in range(4):
#     title_index = html.find(htmltexts[k])
#     start_index = title_index + len(htmltexts[k])
#     end_index = html.find(htmltexts[k + 1])
#     songshtml = html[start_index:end_index]
#     matches = re.findall(html_pattern, songshtml, re.DOTALL)
#     group = songs.Groups(k + 1)
#     for i in range(len(matches)):
#         currentsong = matches[i].splitlines()
#         if len(currentsong) != 23:
#             continue
#         title_match = re.search(title_pattern, currentsong[1])
#         if not title_match:
#             continue
#
#         title = htmlprocess.unescape(title_match.group(1))
#
#         attribute_match = re.search(attribute_pattern, currentsong[3])
#         attribute = attribute_match.group(1).lower()
#         if attribute == "smile":
#             attribute = songs.Attributes(1)
#         elif attribute == "pure":
#             attribute = songs.Attributes(2)
#         elif attribute == "cool":
#             attribute = songs.Attributes(3)
#
#         diffiter = 15
#         diffs = []
#         for j in range(4):
#             number_match = re.search(number_pattern, currentsong[diffiter])
#             if number_match:
#                 diffs.append(int(number_match.group(1)))
#             diffiter += 2
#
#         tempsong = songs.Song(title, group, songs.Attributes(attribute))
#         for j in range(len(diffs)):
#             tempsong.add_difficulty(songs.Difficulties(j + 1), diffs[j])
#         songbook.add_song(tempsong)

# songlist = songbook.get_songs()
# songlist.sort(key=lambda x: x.title)
# for i in songlist:
#     print(i.title)
#     for j in i.difficulties:
#         print("     %s" % j)

# for i, song in enumerate(songbook.songs):
#     print(i, ": ", song.title)




# account1 = accounts.Account(name="Noelle")
# account1.add_score(songbook.songs[229], 0, 208, 75)
# accountlist.append(account1)

# newSong = songs.Song("Hakuchu à la Mode", songs.Groups["HASUNOSORA"], songs.Attributes["PURE"])
# newSong.add_difficulty(1, 6, 183)
# newSong.add_difficulty(2, 8)
# newSong.add_difficulty(3, 10)
# songbook.add_song(newSong)
#
# currentsong = songs.search_songs("Hakuchu à la Mode", songbook)
# accountlist[0].add_score(currentsong, 0, 167, 16)



