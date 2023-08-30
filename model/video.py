import isodate

from infrastructure.google import Google


class Video:
    def __init__(self, video_id: str, google: Google, data=None):
        self.__youtube = google.youtube_client()
        self.video_id = video_id
        self.__data = data

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
        title = self.__data['snippet']['title']
        return title

    def get_description(self):
        self.__initialize_data()
        description = self.__data['snippet']['description']
        return description

    def get_duration(self):
        self.__initialize_data()
        duration_iso = self.__data['contentDetails']['duration']
        duration_in_seconds = isodate.parse_duration(duration_iso).total_seconds()
        return duration_in_seconds

    def get_likes_count(self):
        self.__initialize_data()
        likes = self.__data['statistics']['likeCount']
        return likes

    def get_views_count(self):
        self.__initialize_data()
        views = self.__data['statistics']['viewCount']
        return views

    def get_comment_count(self):
        self.__initialize_data()
        comments = self.__data['statistics']['commentCount']
        return comments
