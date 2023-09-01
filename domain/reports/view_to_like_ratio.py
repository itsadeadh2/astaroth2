from infrastructure.google import Google
from infrastructure.sheets_service import SheetsService, SheetData
from model.video import Video
from model.channel import Channel
import domain.formulas.formulas as formulas
from typing import List

SHORTS_DURATION = 60


class VTLResult:
    name = None
    views = None
    likes = None
    vtl = None

    def __init__(self, data):
        self.name = data['name']
        self.views = data['views']
        self.likes = data['likes']
        self.vtl = data['vtl']


class VTLDataCalculator:
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

    def __init__(self, google: Google):
        self.__gg = google

    def __retrieve_data(self, channel_id, amount):
        channel = Channel(channel_id=channel_id, google=self.__gg)
        return channel.get_videos(amount)

    def __remove_shorts(self, videos_list: List[Video]):
        filtered_videos = []
        for video in videos_list:
            if video.get_duration() > SHORTS_DURATION:
                filtered_videos.append(video)
        return filtered_videos

    def __sort_results(self, results_list: List[VTLResult], reverse=False):
        return sorted(results_list, key=lambda x: x.vtl, reverse=reverse)

    def generate(self, channel_id: str, sample_size=5, sort: str = '', ignore_shorts: bool = True,
                 videos_list: List[Video] = None) -> List[VTLResult]:
        if not videos_list:
            videos_list = self.__retrieve_data(channel_id=channel_id, amount=sample_size)

        if ignore_shorts:
            videos_list = self.__remove_shorts(videos_list=videos_list)

        results_list: List[VTLResult] = []
        for video in videos_list:
            vtl_result = VTLResult(
                {
                    'name': video.get_title(),
                    **formulas.video_to_like(video)
                }
            )
            results_list.append(vtl_result)

        if sort == 'asc':
            results_list = self.__sort_results(results_list=results_list)
        elif sort == 'desc':
            results_list = self.__sort_results(results_list=results_list, reverse=True)

        return results_list


class VTLSheetsReport:
    def __init__(self, channels: List[Channel], google: Google):
        self.__channels = channels
        self.__vtl_calculator = VTLDataCalculator(google=google)
        self.__sheets_service = SheetsService(google=google)
        self.__channels_results = []

    def __retrieve_results(self, sort='asc'):
        if len(self.__channels_results) != 0:
            return
        for channel in self.__channels:
            vtl_result = self.__vtl_calculator.generate(channel_id=channel.channel_id, sort=sort)
            channel_chunk = {
                'channel': channel,
                'vtl': vtl_result
            }
            print('\n')
            print(f"channel: {channel.get_title()}")
            print(f"top vtl: {vtl_result[0].name}")
            self.__channels_results.append(channel_chunk)

    def highest_vtl_per_channel(self, debug=False, sort='asc'):
        self.__retrieve_results()
        sheet_data = SheetData(with_headers=True)

        raw_results = []
        for idx, chunk in enumerate(self.__channels_results):
            channel: Channel = chunk['channel']
            highest_vtl: VTLResult = chunk['vtl'][0]

            row = {
                'Channel Name': channel.get_title(),
                'Video': highest_vtl.name,
                'Likes': highest_vtl.likes,
                'Views': highest_vtl.views,
                'VTL': highest_vtl.vtl,
            }
            raw_results.append(row)
        reverse = False if sort == 'asc' else True
        raw_results = sorted(raw_results, key=lambda x: x['VTL'], reverse=reverse)
        for result in raw_results:
            sheet_data.add_row(result)

        if debug:
            sheet_data.plot_on_terminal()
            return
        self.__sheets_service.update_sheet(sheet_data)
