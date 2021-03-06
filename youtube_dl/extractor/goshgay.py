# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import (
    compat_parse_qs,
)
from ..utils import (
    parse_duration,
)


class GoshgayIE(InfoExtractor):
    _VALID_URL = r'https?://www\.goshgay\.com/video(?P<id>\d+?)($|/)'
    _TEST = {
        'url': 'http://www.goshgay.com/video299069/diesel_sfw_xxx_video',
        'md5': '027fcc54459dff0feb0bc06a7aeda680',
        'info_dict': {
            'id': '299069',
            'ext': 'flv',
            'title': 'DIESEL SFW XXX Video',
            'thumbnail': 're:^http://.*\.jpg$',
            'duration': 79,
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<h2>(.*?)<', webpage, 'title')
        duration = parse_duration(self._html_search_regex(
            r'<span class="duration">\s*-?\s*(.*?)</span>',
            webpage, 'duration', fatal=False))

        flashvars = compat_parse_qs(self._html_search_regex(
            r'<embed.+?id="flash-player-embed".+?flashvars="([^"]+)"',
            webpage, 'flashvars'))
        thumbnail = flashvars.get('url_bigthumb', [None])[0]
        video_url = flashvars['flv_url'][0]

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'age_limit': self._family_friendly_search(webpage),
        }
