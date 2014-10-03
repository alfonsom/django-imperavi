import json
from datetime import datetime

from django.forms.widgets import Textarea
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse
from django.conf import settings

from views import UPLOAD_PATH


IMPERAVI_SETTINGS = getattr(settings, 'IMPERAVI_CUSTOM_SETTINGS', {})
STATIC_URL = getattr(settings, 'STATIC_URL')


class ImperaviWidget(Textarea):

    def __init__(self, *args, **kwargs):
        self.upload_path = kwargs.pop('upload_path', UPLOAD_PATH)# +'/'+str(datetime.now().year)+'/'+str(datetime.now().strftime('%m'))+'/'
        self.file_upload_path = getattr(settings, 'IMPERAVI_FILE_UPLOAD_PATH', {})
        self.imperavi_settings = IMPERAVI_SETTINGS
        super(ImperaviWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        field_id = final_attrs.get('id')
        self.imperavi_settings.update({
            'imageUpload': reverse('imperavi-upload-image', kwargs={'upload_path': self.upload_path}),
            'imageManagerJson': reverse('imperavi-get-json', kwargs={'upload_path': self.upload_path}),
            'fileUpload': reverse('imperavi-upload-file', kwargs={'upload_path': self.file_upload_path}),
            'linkFileUpload': reverse('imperavi-upload-link-file', kwargs={'upload_path': self.upload_path}),
        })
        imperavi_settings = json.dumps(self.imperavi_settings)
        return mark_safe(u"""
            <div style="width: 615px;">
                <textarea%(attrs)s>%(value)s</textarea>
            </div>

            <!-- Plugins -->
            <script src="%(static_url)simperavi/redactor/plugins/video.js"></script>
            <script src="%(static_url)simperavi/redactor/plugins/textdirection.js"></script>
            <script src="%(static_url)simperavi/redactor/plugins/insertGallery.js"></script>
            <script src="%(static_url)simperavi/redactor/plugins/fullscreen.js"></script>
            <script src="%(static_url)simperavi/redactor/plugins/table.js"></script>
            <script src="%(static_url)simperavi/redactor/plugins/imagemanager.js"></script>

            <script>
                $(document).ready(
                    function() {
                        $("#%(id)s").parent().siblings('label').css('float', 'none');
                        $("#%(id)s").height(700);
                        $("#%(id)s").redactor(%(imperavi_settings)s);
                    }
                );
            </script>
            """ % {
                'attrs': flatatt(final_attrs),
                'value': conditional_escape(force_unicode(value)),
                'id': field_id,
                'imperavi_settings': imperavi_settings,
                'static_url': STATIC_URL,
            }
        )
