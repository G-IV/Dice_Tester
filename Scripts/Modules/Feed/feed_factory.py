from Scripts.Modules.Feed import feed, image, multi_image, video, camera

class FeedFactory:
    _registry = {
        "image": image.FeedImage,
        "multi_image": multi_image.FeedMultiImage,
        "video": video.FeedVideo,
        "camera": camera.FeedCamera
    }

    @classmethod
    def create_feed(cls, feed_type: str, **kwargs) -> feed.Feed:
        feed_class = cls._registry.get(feed_type)
        if not feed_class:
            raise ValueError(f"Feed type '{feed_type}' is not registered.")
        return feed_class(**kwargs)