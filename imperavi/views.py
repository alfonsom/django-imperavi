import hashlib
import json
import os.path
import imghdr
import string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.utils.encoding import smart_str
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings

from boto.s3.connection import S3Connection

from forms import ImageForm, FileForm

from sorl.thumbnail import get_thumbnail


UPLOAD_PATH = getattr(settings, 'IMPERAVI_UPLOAD_PATH', 'imperavi/')
ACCESS_KEY = getattr(settings, 'AWS_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')

@require_POST
@csrf_exempt
@user_passes_test(lambda user: user.is_staff)
def upload_image(request, upload_path=None):
    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        image = form.cleaned_data['file']
        if image.content_type not in ['image/png', 'image/jpg', 'image/jpeg', 'image/pjpeg']:
            return HttpResponse('Bad image format')
        image_name, extension = os.path.splitext(image.name)
        m = hashlib.md5(smart_str(image_name))
        hashed_name = '{0}{1}'.format(m.hexdigest(), extension)
        image_path = default_storage.save(os.path.join(upload_path or UPLOAD_PATH, hashed_name), image)
        image_url = default_storage.url(image_path)
        return HttpResponse(json.dumps({'filelink': image_url}))
    return HttpResponseForbidden()


@user_passes_test(lambda user: user.is_staff)
def uploaded_images_json(request, upload_path=None):
    upload_path = upload_path or UPLOAD_PATH
    results = list()
    path = os.path.join(settings.AMAZON_URL, upload_path)
    conn = S3Connection(ACCESS_KEY,SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(BUCKET_NAME)
    # for key in bucket.list():
    #     print key.name.encode('utf-8')
    #         
        
    results = list()
    folder = 'init'
    for key in bucket.list('image/library/'):
        name = key.name.replace('image/library/','')
        
        a = string.split(name,'/')
        if a[0]==folder:
            image_url = settings.AMAZON_URL+key.name
            # thumb = get_thumbnail(image_url, '100x74')
            results.append({'thumb':image_url, 'image':image_url, 'folder': folder })
        else:
            folder = a[0]
    
    # if os.path.isdir(path):
    #     for image in os.listdir(path):
    #         image_path = '{0}{1}'.format(path, smart_str(image))
    #         if not os.path.isdir(image_path) and imghdr.what(image_path):
    #             thumb = get_thumbnail(image_path, '100x74', crop='center')
    #             image_url = os.path.join(settings.AMAZON_URL, upload_path, image)
    #             results.append({'thumb': thumb.url, 'image': image_url})
    if results:
        return HttpResponse(json.dumps(results))
    return HttpResponse('{}')


@require_POST
@csrf_exempt
@user_passes_test(lambda user: user.is_staff)
def upload_file(request, upload_path=None, upload_link=None):
    form = FileForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_file = form.cleaned_data['file']
        path = os.path.join(upload_path or UPLOAD_PATH, uploaded_file.name)
        image_path = default_storage.save(path, uploaded_file)
        image_url = default_storage.url(image_path)
        if upload_link:
            return HttpResponse(image_url)
        return HttpResponse(json.dumps({'filelink': image_url, 'filename': uploaded_file.name}))
    return HttpResponseForbidden()
