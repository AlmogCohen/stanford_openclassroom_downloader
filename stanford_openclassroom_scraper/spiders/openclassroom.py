# -*- coding: utf-8 -*-
import os
import re

import scrapy
from scrapy.http.request import Request
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class OpenclassroomSpider(scrapy.Spider):
    name = "openclassroom"
    allowed_domains = ["openclassroom.stanford.edu"]
    start_urls = (
        'http://openclassroom.stanford.edu/MainFolder/courses/MachineLearning/course.xml',
    )
    link_extractor = LxmlLinkExtractor
    VIDEO_BASE_URL = 'http://openclassroom.stanford.edu/MainFolder/courses/MachineLearning/videos/%s'
    OUTPUT_FOLDER = 'ML'

    def parse(self, response):
        file_pattern = '<file>(.+?)<\/file>'
        for filename in re.findall(file_pattern, response.body):
            filename = '%s.mp4' % filename
            yield Request(self.VIDEO_BASE_URL % filename, callback=self.download_mp4, meta={'filename': filename})

    def download_mp4(self, response):
        folder_path = os.path.join('.', self.OUTPUT_FOLDER)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with file(os.path.join(folder_path, response.meta['filename']), 'wb') as f:
            f.write(response.body)

