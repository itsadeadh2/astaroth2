import os

from infrastructure.google import Google
from infrastructure.openai import OpenAi
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
    transcript = None
    with open('output.json', 'rb') as file:
        transcript = file.read().decode('utf-8')
    answer = OpenAi.analize_video(transcript=transcript)
    print(answer)
    debug = True if os.getenv('DEBUG') == '1' else False
    competitors_ids = load_competitors()
    if debug:
        competitors_ids = competitors_ids[:1]
    channels_list = Channel.retrieve_from_ids_list(ids_list=competitors_ids, google=gg)
    for channel in channels_list:
        print("\n=======================================")
        print(f"Channel Name: {channel.get_title()}")
        videos = channel.get_videos(1)
        last_video = videos[0]
        print(f"Last video: {last_video.get_title()}")
        print("=======================================")
        last_video.get_caption()
