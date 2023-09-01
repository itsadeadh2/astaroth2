import os

from domain.reports.view_to_like_ratio import VTLSheetsReport
from infrastructure.google import Google
from infrastructure.openai import OpenAi
from model.channel import Channel
import matplotlib.pyplot as plt


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
    debug = True if os.getenv('DEBUG') == '1' else False
    competitors_ids = load_competitors()
    if debug:
        competitors_ids = competitors_ids[:1]
    channels_list = Channel.retrieve_from_ids_list(ids_list=competitors_ids, google=gg)

    report = VTLSheetsReport(channels=channels_list, google=gg)
    report.videos_ranked_by_vtl(sample_size=100)
    report.channels_ranked_by_vtl(sample_size=100)