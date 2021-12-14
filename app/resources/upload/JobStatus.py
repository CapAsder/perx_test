import rq
from flask_restful import Resource
from redis.client import Redis
from rq.job import Job

from app import app
from app.utils.helpers import auth_only, error, ok


class JobStatus(Resource):
    __route__ = '/job_status/<string:job_id>'

    @auth_only()
    def get(self, job_id):
        job = Job.fetch(
            job_id,
            connection=Redis.from_url("redis://{0}:{1}".format(app.config['REDIS_HOST'], app.config['REDIS_PORT']))
        )
        result = {'status': job.get_status()}
        needed_fields = ['started_at', 'ended_at', 'progress', 'result']
        for field in needed_fields:
            if field in job.meta:
                result[field] = job.meta[field]
        return ok(result), 200
