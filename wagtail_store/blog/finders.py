import re

from wagtail.embeds.finders.oembed import OEmbedFinder


class PeerTubeFinder(OEmbedFinder):

    ENDPOINT = '/services/oembed'

    # TODO - this should be configurable from admin - TO be added with setup extension
    PATTERNS = [
        re.compile(
            r'^(https?://[^/]+)/w/.*'
        )
    ]

    def _get_endpoint(self, url):
        for pattern in self.PATTERNS:
            m = pattern.match(url)
            if m is not None:
                return m.group(1) + self.ENDPOINT


embed_finder_class = PeerTubeFinder
