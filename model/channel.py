from typing import List

from infrastructure.google import Google
from model.video import Video


class Channel:
    __data = None

    @staticmethod
    def init_channels_from_id_list(ids_list: [str], google: Google):
        channels_list = []
        for channel_id in ids_list:
            channel = Channel(channel_id=channel_id, google=google)
            channels_list.append(channel)
        return channels_list

    def __init__(self, channel_id: str, google: Google):
        self.__gg = google
        self.__youtube = google.youtube_client()
        self.channel_id = channel_id

    def __initialize_data(self):
        if self.__data:
            return
        request = self.__youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=self.channel_id
        )
        self.__data = request.execute()

    def get_title(self):
        self.__initialize_data()
        title = self.__data['items'][0]['snippet']['title']
        return title

    def get_description(self):
        self.__initialize_data()
        description = self.__data['items'][0]['snippet']['description']
        return description

    def get_subscribers_count(self):
        self.__initialize_data()
        subscribers = self.__data['items'][0]['statistics']['subscriberCount']
        return subscribers

    def get_views_count(self):
        self.__initialize_data()
        views = self.__data['items'][0]['statistics']['viewCount']
        return views

    def get_videos_count(self):
        self.__initialize_data()
        videos = self.__data['items'][0]['statistics']['videoCount']
        return videos

    def get_videos(self, max_results=10) -> List[Video]:
        search_request = self.__youtube.search().list(
            part="snippet",
            channelId=self.channel_id,
            order="date",
            maxResults=max_results
        )
        videos_data = search_request.execute()
        videos_list = []
        for entry in videos_data['items']:
            video = Video(video_id=entry['id']['videoId'], google=self.__gg)
            videos_list.append(video)

        return videos_list
