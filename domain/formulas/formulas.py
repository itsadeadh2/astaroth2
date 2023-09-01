from model.video import Video


def video_to_like(video: Video):
    views = int(video.get_views_count())
    likes = int(video.get_likes_count())
    vtl = views / likes
    return {"views": views, "likes": likes, "vtl": vtl}
