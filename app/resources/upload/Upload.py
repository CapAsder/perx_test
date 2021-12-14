import time
from pathlib import Path

from flask import request
from flask_restful import Resource

from app import app, tasks
from app.utils.helpers import auth_only, error, ok
import hashlib
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


class Upload(Resource):
    __route__ = '/upload'

    def get(self):
        return ok()

    @auth_only()
    def post(self):
        if 'file' not in request.files:
            return error('bad_request'), 403
        file = request.files['file']
        if file.filename == '':
            return error('bad_filename'), 403
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            m = hashlib.md5()
            m.update("md5{0}.{1}".format(time.time(), app.config['SECRET_KEY']).encode('utf-8'))
            filename = "{0}.{1}".format(m.hexdigest(), ext)
            try:
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(full_path)
                from redis import Redis
                import rq
                queue = rq.Queue('upload_file_tasks',
                                 connection=Redis.from_url("redis://{0}:{1}".format(
                                     app.config['REDIS_HOST'], app.config['REDIS_PORT'])),
                                 default_timeout=600)
                job = queue.enqueue('app.tasks.upload_file.start', filename)
                return ok({'status': 'file uploaded', 'job_id': job.get_id()}), 200
            except Exception as exc:
                print(exc)
                return error('Internal error'), 500

        return error('bad_request'), 403