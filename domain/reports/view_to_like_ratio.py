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

    def __retrieve_data(self, channel_id, sample_size, ignore_shorts=True):
        channel = Channel(channel_id=channel_id, google=self.__gg)
        min_duration = 60 if ignore_shorts else 1
        return channel.get_videos(max_results=sample_size, min_duration=min_duration)

    def __sort_results(self, results_list: List[VTLResult], reverse=False):
        return sorted(results_list, key=lambda x: x.vtl, reverse=reverse)

    def generate(self, channel_id: str, sample_size=5, sort: str = '', ignore_shorts: bool = True,
                 videos_list: List[Video] = None) -> List[VTLResult]:
        if not videos_list:
            videos_list = self.__retrieve_data(channel_id=channel_id, sample_size=sample_size, ignore_shorts=True)

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

    def __retrieve_results(self, sample_size, sort='asc'):
        if len(self.__channels_results) != 0:
            return
        for channel in self.__channels:
            vtl_result = self.__vtl_calculator.generate(channel_id=channel.channel_id, sort=sort, sample_size=sample_size)
            channel_chunk = {
                'channel': channel,
                'vtl': vtl_result
            }
            print('\n')
            print(f"channel: {channel.get_title()}")
            print(f"top vtl: {vtl_result[0].name}")
            self.__channels_results.append(channel_chunk)

    def channels_ranked_by_vtl(self, sample_size, debug=False, sort='asc'):
        self.__retrieve_results(sample_size=sample_size)
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
        sheets_page_name = "All Channels"
        if sheets_page_name not in self.__sheets_service.get_pages_names():
            self.__sheets_service.add_page(page_name=sheets_page_name)
        self.__sheets_service.update_sheet(sheet_data, page_name=sheets_page_name)

    def videos_ranked_by_vtl(self, sample_size, sort='asc'):
        self.__retrieve_results(sample_size=sample_size)
        available_pages = self.__sheets_service.get_pages_names()
        for idx, chunk in enumerate(self.__channels_results):
            raw_results = []
            channel: Channel = chunk['channel']
            vtl_result_list: List[VTLResult] = chunk['vtl']
            sheet_data = SheetData(with_headers=True)

            for vtl_result in vtl_result_list:
                row = {
                    'Video': vtl_result.name,
                    'Likes': vtl_result.likes,
                    'Views': vtl_result.views,
                    'VTL': vtl_result.vtl,
                }
                raw_results.append(row)

            reverse = False if sort == 'asc' else True
            raw_results = sorted(raw_results, key=lambda x: x['VTL'], reverse=reverse)
            for result in raw_results:
                sheet_data.add_row(result)
            if channel.get_title() not in available_pages:
                self.__sheets_service.add_page(channel.get_title())
            self.__sheets_service.update_sheet(sheet_data, page_name=channel.get_title())
