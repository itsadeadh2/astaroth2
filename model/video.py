import json

import isodate

from infrastructure.google import Google
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List

class Video:
    def __init__(self, video_id: str, google: Google, data=None):
        self.__gg = google
        self.__youtube = google.youtube_client()
        self.video_id = video_id
        self.__data = data

    @staticmethod
    def retrieve_from_ids_list(ids_list: [str], google: Google):
        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        max_ids_allowed = 20
        id_chunks = list(divide_chunks(ids_list, max_ids_allowed))
        videos_list = []

        for chunked_id_list in id_chunks:
            ids_string = ''
            for video_id in chunked_id_list:
                ids_string += f'{video_id},'

            youtube = google.youtube_client()
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=ids_string,
            )
            response = request.execute()
            for entry in response['items']:
                video = Video(video_id=entry['id'], google=google, data=entry)
                videos_list.append(video)
        return videos_list

    @staticmethod
    def filter_by_min_duration(videos, min_duration=60):
        filtered_videos = []
        for video in videos:
            if video.get_duration() > min_duration:
                filtered_videos.append(video)
        return filtered_videos

    def __initialize_data(self):
        if self.__data:
            return
        request = self.__youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=self.video_id
        )
        response = request.execute()
        self.__data = response['items'][0]

    def get_title(self):
        self.__initialize_data()
        return self.__data['snippet']['title']

    def get_description(self):
        self.__initialize_data()
        return self.__data['snippet']['description']

    def get_duration(self):
        self.__initialize_data()
        duration_iso = self.__data['contentDetails']['duration']
        duration_in_seconds = isodate.parse_duration(duration_iso).total_seconds()
        return duration_in_seconds

    def get_likes_count(self):
        self.__initialize_data()
        try:
            return self.__data['statistics']['likeCount']
        except:
            return 1

    def get_views_count(self):
        self.__initialize_data()
        return self.__data['statistics']['viewCount']

    def get_comment_count(self):
        self.__initialize_data()
        return self.__data['statistics']['commentCount']

    def get_caption(self):
        transcript = YouTubeTranscriptApi.get_transcript(video_id=self.video_id)
        with open("output.json", "w", encoding='utf-8') as file:
            file.write(json.dumps(transcript, ensure_ascii=False))
        return transcript
