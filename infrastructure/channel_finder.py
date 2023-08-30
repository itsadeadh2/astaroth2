from typing import List
from infrastructure.google import Google
from model.channel import Channel


class ChannelFinder:
    def __init__(self, google: Google):
        self.__gg = google
        self.__youtube = google.youtube_client()

    def retrieve_channels(self, channel_names: str) -> List[Channel]:
        channels = []
        for channel in channel_names:
            request = self.__youtube.search().list(
                part="snippet",
                type="channel",
                q=channel
            )
            response = request.execute()
            channel_id = response['items'][0]['id']['channelId']
            channel = Channel(channel_id=channel_id, google=self.__gg)
            channels.append(channel)

        return channels
