import os

from domain.reports.view_to_like_ratio import VTLReport
from infrastructure.google import Google
from infrastructure.openai import OpenAi
from model.channel import Channel


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
    vtl_report = VTLReport(google=gg, target_channel_id=channels_list[0].channel_id)
    result = vtl_report.generate()
    print(result)
    from rich.progress import track

    from rich.console import Console
    from rich.table import Table
    import json

    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Subs count")
    table.add_column("Videos count")
    table.add_column("Total Views")
    table.add_column("Latest Video")

    transcriptions = []
    with console.status("[bold green]Processing channels...") as status:
        for channel in channels_list:
            video_list = channel.get_videos(1)
            last_video = video_list[0]
            table.add_row(
                channel.get_title(),
                channel.get_subscribers_count(),
                channel.get_videos_count(),
                channel.get_views_count(),
                last_video.get_title()
            )
            transcription_object = {
                "channel": channel.get_title(),
                "transcription": last_video.get_caption()
            }
            transcriptions.append(transcription_object)
            console.log(f'{channel.get_title()} - complete')

    console.log("Processing complete!")
    console.print(table)
    if input("Do you want to run the analysis for the videos on GPT-4? ").lower() == 'y':
        with console.status("[bold blue]Running analysis through GPT-4...") as status:
            for transcription in transcriptions:
                analysis = OpenAi.analize_video(json.dumps(transcription['transcription'])[0:5000])
                with open(f'analysis/{transcription["channel"]}.txt', 'w', encoding='utf-8') as file:
                    file.write(analysis)
                console.log("Done")
    console.print("Reports can be found on the [bold green]analysis[/bold green] folder")
