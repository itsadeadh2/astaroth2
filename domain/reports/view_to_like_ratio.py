from infrastructure.google import Google
from model.video import Video
from model.channel import Channel
import domain.formulas.formulas as formulas
from typing import List

SHORTS_DURATION = 60


class VTLReport:
    """
    VTL (View To Like) Report
    This is a report that orders the video results based on
    the ratio of the video views divided by it's likes.
    The question it answers is:
    How many views is it required for the video to get one like?
    So a video with 20 views and 2 likes:
    20v/2l = 10VTL
    Meaning every 10 views that video got one like.
    """

    def __init__(self, google: Google, target_channel_id: str = None, videos_list: List[Video] = None):
        """
        Initializes a VTLRatio Report instance.
        You need to either pass a target_channel_id or a pre-fetched videos_list for this report to work.
        When passing both, the report will prioritize the videos_list, which means no additional requests for
        the channel_id will be made.
        Args:
            google: Google (required) The Google Class instance to use to interact with Youtube API
            target_channel_id: str (optional) The target channel id you want to run the report against
            videos_list: List[Video] (Optional) A pre-fetched list of Video objects you want to run the report against
        """
        self.__gg = google
        self.__channel_id = target_channel_id
        self.__videos_list = videos_list
        self.__validate_required_params()

    def __validate_required_params(self):
        if not self.__channel_id and not self.__videos_list:
            raise Exception(
                "No channel_id or videos_list found. You need to specify at least one of them for this report to work.")

    def __retrieve_data(self, amount):
        if self.__videos_list:
            return
        channel = Channel(channel_id=self.__channel_id, google=self.__gg)
        self.__videos_list = channel.get_videos(amount)

    def __remove_shorts(self):
        filtered_videos = []
        for video in self.__videos_list:
            if video.get_duration() > SHORTS_DURATION:
                filtered_videos.append(video)
        self.__videos_list = filtered_videos

    def generate(self, sample_size=5, ignore_shorts: bool = True):
        self.__retrieve_data(amount=sample_size)
        if ignore_shorts:
            self.__remove_shorts()
        results_list = []
        for video in self.__videos_list:
            vtl_result = {
                'Name': video.get_title(),
                **formulas.video_to_like(video)
            }
            results_list.append(vtl_result)

        return results_list
