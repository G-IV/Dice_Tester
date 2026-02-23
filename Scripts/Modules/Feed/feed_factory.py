from Scripts.Modules.Feed import feed, image, multi_image, video, cam

class FeedFactory:
    _registry = {
        "image": image.Feed,
        "multi_image": multi_image.Feed,
        "video": video.Feed,
        "cam": cam.Feed
    }

    @classmethod
    def create_feed(cls, feed_type: str, **kwargs) -> feed.Feed:
        feed_class = cls._registry.get(feed_type)
        if not feed_class:
            raise ValueError(f"Feed type '{feed_type}' is not registered.")
        return feed_class(**kwargs)