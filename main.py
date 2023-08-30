import os

from infrastructure.google import Google
from model.channel import Channel


def load_competitors():
    dirname = os.path.dirname(__file__)
    competitors_path = os.path.join(dirname, 'config/competitors.txt')
    competitors_list = []
    with open(competitors_path, 'rb') as file:
        content = file.read().decode('utf-8')
        entries = content.split('\n')
        for competitor in entries:
            competitor = competitor.split('=')[1].strip()
            competitors_list.append(competitor)
    return competitors_list


if __name__ == "__main__":
    gg = Google()
    competitors_ids = load_competitors()
    channels_list = Channel.init_channels_from_id_list(ids_list=competitors_ids, google=gg)
    for channel in channels_list:
        print("\n=======================================")
        print(f"Channel Name: {channel.get_title()}")
        videos = channel.get_videos(1)
        last_video = videos[0]
        print(f"Last video: {last_video.get_title()}")
        print("=======================================")
