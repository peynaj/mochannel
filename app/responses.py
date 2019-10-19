import json
from rest_framework.response import Response


def bad_request_json_response(message='', status=None):
    data = dict(message=message)
    resp = Response()
    resp.status_code = status or 400
    resp.content_type = 'application/json'
    resp.data = json.dumps(data)
    return resp


def not_found_json_response(message='', status=None):
    data = dict(message=message)
    resp = Response()
    resp.status_code = status or 404
    resp.content_type = 'application/json'
    resp.data = json.dumps(data)
    return resp


def successful_json_resonse(message='', status=None):
    data = dict(message=message)
    resp = Response()
    resp.status_code = status or 200
    resp.content_type = 'application/json'
    resp.data = json.dumps(data)
    return resp

