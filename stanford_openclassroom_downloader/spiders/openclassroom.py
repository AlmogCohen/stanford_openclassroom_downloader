# -*- coding: utf-8 -*-
import os
import re

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http.request import Request
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.project import get_project_settings

DIVIDER_STRING = '#' * 30


class OpenclassroomSpider(scrapy.Spider):
    name = "openclassroom"

    COURSE_PATTERN = '<td><a href="(.+?)\/">.+?\/<\/a><\/td>'
    OPEN_CLASSROOM_BASE = 'http://openclassroom.stanford.edu/MainFolder/courses'
    COURSE_MANIFEST_URL = OPEN_CLASSROOM_BASE + '/%s/course.xml'
    VIDEO_BASE_TEMPLATE = OPEN_CLASSROOM_BASE + '/%s/videos/'

    start_urls = [OPEN_CLASSROOM_BASE]
    allowed_domains = ["openclassroom.stanford.edu"]
    link_extractor = LxmlLinkExtractor

    def __init__(self, course=None, *args, **kwargs):
        """
        Fetches the course list if course if None, else - download all the lectures of the provided course.
        :param course: number of the course printed by this script, or the full name of it
        """
        super(OpenclassroomSpider, self).__init__(*args, **kwargs)
        self.course = course
        self.video_base_url = None

    def parse(self, response):
        """
        Parse the courses list then decide if to show the list to the user of to go and download the videos
        according to the user's course selection
        """
        courses = sorted(re.findall(self.COURSE_PATTERN, response.body, re.M))
        # Translate the user selection to the course string name
        if isinstance(self.course, str) and self.course.isdigit():
            assert 0 <= int(self.course) <= len(courses) - 1, "Course ID selection is not in selection range"
            self.course = courses[int(self.course)]

        # good course selection
        if self.course in courses:
            yield Request(self.COURSE_MANIFEST_URL % self.course, callback=self.parse_course_manifest)

        # The user had invalid selection, print the lectures list
        else:
            print DIVIDER_STRING
            # print the invalid selection to the user if he selected something
            if self.course is not None:
                print "Invalid course selection: %s" % self.course

            print "Possible course selections are: (course ID or the course name)"
            for course_id, course_name in enumerate(courses):
                print "%s. %s" % (course_id, course_name)
            print "Run your selection with 'scrapy crawl openclassroom -a course <your-selection>'"
            print DIVIDER_STRING

    def parse_course_manifest(self, response):
        """Prase the manifest file of the given course to get the video names"""
        file_pattern = '<file>(.+?)<\/file>'
        for filename in re.findall(file_pattern, response.body):
            filename = '%s.mp4' % filename
            yield Request((self.VIDEO_BASE_TEMPLATE % self.course) + filename, callback=self.download_mp4, meta={'filename': filename})

    def download_mp4(self, response):
        folder_path = os.path.join('.', self.course + '_videos')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with file(os.path.join(folder_path, response.meta['filename']), 'wb') as f:
            f.write(response.body)

if __name__ == "__main__":
    p = CrawlerProcess(get_project_settings())
    p.crawl(OpenclassroomSpider)
    p.start()