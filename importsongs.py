import pandas as pd
import songs

songsheet = pd.read_excel('songsheet.xlsx', sheet_name='MUSIC')
diffsheet = pd.read_excel('songsheet.xlsx', sheet_name='LEVEL')

songs_list = songs.Songbook()

for index, row in songsheet.iloc[0:].iterrows():
    newsong = songs.Song(row['id'], row['name'], songs.Groups(row['bandCategory']))
    print(f"Adding song {newsong.title} with ID {row['id']}")
    songs_list.add_song(newsong)

print("Adding diffs.")
for index, row in diffsheet.iloc[1:].iterrows():
    print(f"Adding difficulty {row['levelNumber']} to {row['masterMusicId']}")
    song = songs.search_songs_id(int(row['masterMusicId']), songs_list)
    song.add_difficulty(int(row['level']), int(row['levelNumber']), int(row['fullCombo']))

songs.save_songs(songs_list.songs, 'songs.json')
