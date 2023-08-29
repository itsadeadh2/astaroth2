from infrastructure.google import Google
from model.channel import Channel


if __name__ == "__main__":
    gg = Google()
    channel = Channel(channel_id='', google=gg)
    c_title = channel.get_title()
    c_description = channel.get_description()

    videos = channel.get_videos(5)
    first = videos[0]
    duration = first.get_duration()
    likes_count = first.get_likes_count()
    views_count = first.get_views_count()
    comments = first.get_comment_count()
    v_title = first.get_title()
    v_description = first.get_description()

    print(videos)
