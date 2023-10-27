""" plyrXBlock main Python class"""

import pkg_resources
from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean
from xblock.fragment import Fragment


class plyrXBlock(XBlock):

    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = "video"

    '''
    Fields
    '''
    display_name = String(display_name="Display Name",
                          default="Video",
                          scope=Scope.settings,
                          help="This name appears in the horizontal navigation at the top of the page.")

    url = String(display_name="Video URL",
                 default="https://dash.akamaized.net/envivio/EnvivioDash3/manifest.mpd",
                 scope=Scope.content,
                 help="The URL for your video.")

    allow_download = Boolean(display_name="Video Download Allowed",
                             default=True,
                             scope=Scope.content,
                             help="Allow students to download this video.")

    source_text = String(display_name="Source document button text",
                         default="",
                         scope=Scope.content,
                         help="Add a download link for the source file of your video. Use it for example to provide the PowerPoint or PDF file used for this video.")

    source_url = String(display_name="Source document URL",
                        default="",
                        scope=Scope.content,
                        help="Add a download link for the source file of your video. Use it for example to provide the PowerPoint or PDF file used for this video.")

    start_time = String(display_name="Start time",
                        default="",
                        scope=Scope.content,
                        help="The start and end time of your video. Equivalent to 'video.mp4#t=startTime,endTime' in the url.")

    end_time = String(display_name="End time",
                      default="",
                      scope=Scope.content,
                      help="The start and end time of your video. Equivalent to 'video.mp4#t=startTime,endTime' in the url.")

    '''
    Util functions
    '''

    def load_resource(self, resource_path):
        """
        Gets the content of a resource
        """
        resource_content = pkg_resources.resource_string(
            __name__, resource_path)
        # return unicode(resource_content, 'utf-8')
        return resource_content.decode('utf-8')

    def render_template(self, template_path, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = self.load_resource(template_path)
        return Template(template_str).render(Context(context))

    '''
    Main functions
    '''

    def student_view(self, context=None):
        """
        The primary view of the XBlock, shown to students
        when viewing courses.
        """
        fullUrl = self.url
        if self.start_time != "" and self.end_time != "":
            fullUrl += "#t=" + self.start_time + "," + self.end_time
        elif self.start_time != "":
            fullUrl += "#t=" + self.start_time
        elif self.end_time != "":
            fullUrl += "#t=0," + self.end_time

        context = {
            'display_name': self.display_name,
            'url': fullUrl,
            'allow_download': self.allow_download,
            'source_text': self.source_text,
            'source_url': self.source_url
        }

        html = self.render_template('static/html/plyr_view.html', context)

        frag = Fragment(html)
        frag.add_css(self.load_resource("static/css/plyr.css"))

        '''
        No need to load dash.all.min.js as I have already added it from cdn in plyr_view.html
        frag.add_javascript(self.load_resource("static/js/dash.all.debug.js"))
        <script src="https://cdn.dashjs.org/latest/dash.all.min.js"></script>
        '''
        frag.add_javascript(self.load_resource("static/js/plyr_view.js"))
        frag.initialize_js('plyrXBlockInitView')
        return frag

    def studio_view(self, context=None):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        context = {
            'display_name': self.display_name,
            'url': self.url,
            'allow_download': self.allow_download,
            'source_text': self.source_text,
            'source_url': self.source_url,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
        html = self.render_template('static/html/plyr_edit.html', context)

        frag = Fragment(html)
        frag.add_javascript(self.load_resource("static/js/plyr_edit.js"))
        frag.initialize_js('plyrXBlockInitStudio')
        return frag

    @XBlock.json_handler
    def save_plyr(self, data, suffix=''):
        """
        The saving handler.
        """
        self.display_name = data['display_name']
        self.url = data['url']
        # Str to Bool translation
        self.allow_download = True if data['allow_download'] == "True" else False
        self.source_text = data['source_text']
        self.source_url = data['source_url']
        self.start_time = ''.join(
            data['start_time'].split())  # Remove whitespace
        self.end_time = ''.join(data['end_time'].split())  # Remove whitespace

        return {
            'result': 'success',
        }
