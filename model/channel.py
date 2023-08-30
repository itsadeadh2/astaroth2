from typing import List

from infrastructure.google import Google
from model.video import Video


class Channel:
    __data = None

    @staticmethod
    def init_channels_from_id_list(ids_list: [str], google: Google):
        ids_string = ''
        for channel_id in ids_list:
            ids_string += f'{channel_id},'
        
        youtube = google.youtube_client()
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=ids_string
        )
        channels_data = request.execute()
        channels_list = []
        for entry in channels_data['items']:
            channel = Channel(channel_id=entry['id'], google=google, data=entry)
            channels_list.append(channel)
        return channels_list

    def __init__(self, channel_id: str, google: Google, data=None):
        self.__gg = google
        self.__youtube = google.youtube_client()
        self.channel_id = channel_id
        self.__data = data

    def __initialize_data(self):
        if self.__data:
            return
        request = self.__youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=self.channel_id
        )
        response = request.execute()
        self.__data = response['items'][0]

    def get_title(self):
        self.__initialize_data()
        title = self.__data['snippet']['title']
        return title

    def get_description(self):
        self.__initialize_data()
        description = self.__data['snippet']['description']
        return description

    def get_subscribers_count(self):
        self.__initialize_data()
        subscribers = self.__data['statistics']['subscriberCount']
        return subscribers

    def get_views_count(self):
        self.__initialize_data()
        views = self.__data['statistics']['viewCount']
        return views

    def get_videos_count(self):
        self.__initialize_data()
        videos = self.__data['statistics']['videoCount']
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
        video_ids = [entry['id']['videoId'] for entry in videos_data['items']]
        ids_string = ''
        for video_id in video_ids:
            ids_string += f'{video_id},'

        videos_details_request = self.__youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=ids_string,
        )
        videos_data = videos_details_request.execute()
        for entry in videos_data['items']:
            video = Video(video_id=entry['id'], google=self.__gg, data=entry)
            videos_list.append(video)

        return videos_list
