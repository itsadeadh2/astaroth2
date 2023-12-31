from typing import List

from infrastructure.google import Google
from model.video import Video


class Channel:
    __data = None

    def __init__(self, channel_id: str, google: Google, data=None):
        self.__gg = google
        self.__youtube = google.youtube_client()
        self.channel_id = channel_id
        self.__data = data

    def __initialize_data(self):
        if self.__data:
            return
        request = self.__youtube.channels().list(part="snippet,contentDetails,statistics", id=self.channel_id)
        response = request.execute()
        self.__data = response['items'][0]
        func(self, *args, **kwargs)

    @staticmethod
    def retrieve_from_ids_list(ids_list: [str], google: Google):
        ids_string = ''
        for channel_id in ids_list:
            ids_string += f'{channel_id},'

        youtube = google.youtube_client()
        request = youtube.channels().list(part="snippet,contentDetails,statistics", id=ids_string)
        channels_data = request.execute()
        channels_list = []
        for entry in channels_data['items']:
            channel = Channel(channel_id=entry['id'], google=google, data=entry)
            channels_list.append(channel)
        return channels_list

    def get_title(self):
        self.__initialize_data()
        return self.__data['snippet']['title']

    def get_description(self):
        self.__initialize_data()
        return self.__data['snippet']['description']

    def get_subscribers_count(self):
        self.__initialize_data()
        return self.__data['statistics']['subscriberCount']

    def get_views_count(self):
        self.__initialize_data()
        return self.__data['statistics']['viewCount']

    def get_videos_count(self):
        self.__initialize_data()
        return self.__data['statistics']['videoCount']

    def get_videos(self, max_results=10, min_duration=60) -> List[Video]:
        videos_list: List[Video] = []
        next_page_token = None
        more_results = True
        while len(videos_list) < max_results and more_results:
            params = {
                "part": "snippet",
                "channelId": self.channel_id,
                "order": "date",
                "maxResults": max_results,
                "type": "video"
            }
            if next_page_token:
                params['pageToken'] = next_page_token
            search_request = self.__youtube.search().list(**params)
            videos_data = search_request.execute()
            next_page_token = videos_data.get('nextPageToken', '')
            if not next_page_token:
                more_results = False
            video_ids = [entry['id']['videoId'] for entry in videos_data['items']]
            videos_list += Video.retrieve_from_ids_list(ids_list=video_ids, google=self.__gg)
            videos_list = Video.filter_by_min_duration(videos_list, min_duration=min_duration)

        return videos_list[:max_results]

