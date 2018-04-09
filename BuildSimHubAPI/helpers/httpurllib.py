import ssl
import json
try:
    import httplib
except ImportError:
    import http.client as httplib

import urllib


class HTTPConnect:
    def __init__(self, status_code, response_obj):
        self._status_code = status_code
        self._response_error = ""
        if type(response_obj) is bytes:
            response_obj = response_obj.decode("utf-8")

        if type(response_obj) is str:
            try:
                self._response = json.loads(response_obj)
            except:
                self._response = response_obj
        elif type(response_obj) is dict:
            try:
                self._response = json.loads(json.dumps(response_obj))
            except:
                self._response = response_obj
        else:
            self._response = response_obj

    @property
    def status_code(self):
        return self._status_code

    def json(self):
        return self._response

    def set_error(self, error):
        self._response_error = error

    def get_error(self):
        return self._response_error

    def iter_content(self, chunk_size=1024):
        contents = []

        try:
            chunk = self.response.read(chunk_size)
            while len(chunk) > 0:
                contents.append(chunk)
                chunk = self.response.read(chunk_size)
        except:
            print('ERROR: response object cannot be iter read')
        return contents


def __split_path(path):
    double_slash_idx = path.find('//')
    if double_slash_idx < 0:
        return {'status': 'error', 'error_msg': 'path missing protocol'}

    protocol = path[:double_slash_idx + 2]
    protocol.lower()

    if protocol == 'https://':
        is_ssl = True
        path = path[8:]  # remove https:// part
    elif protocol == 'http://':
        is_ssl = False
        path = path[7:]  # remove http:// part
    else:
        return {'status': 'error', 'error_msg': 'path protocol is not https or http'}

    slash_idx = path.find('/')
    if slash_idx < 0:
        host = path
        req_path = ""
    else:
        host = path[:slash_idx]
        req_path = path[slash_idx:]

    if is_ssl:
        conn = httplib.HTTPSConnection(host, context=ssl._create_unverified_context())
    else:
        conn = httplib.HTTPConnection(host)

    return {'status': 'success', 'conn': conn, 'req_path': req_path}


def __encode_multipart_formdata(fields, files):
    boundary = 'BuildSimHub_boundary_string'
    crlf = '\r\n'
    form = []

    for (key, value) in fields.items():
        form.append('--' + boundary)
        form.append('Content-Disposition: form-data; name="%s"' % key)
        form.append('')
        form.append(str(value))
    for (key, f) in files.items():
        form.append('--' + boundary)

        # 3.6 will upload the full dir
        # this code extract the file name
        filename = f.name
        slash = max(filename.rfind('/'), filename.rfind('\\'))
        if slash >= 0:
            filename = filename[slash + 1:]

        form.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        form.append('Content-Type: application/octet-stream')
        form.append('')
        form.append(f.read())
    form.append('--' + boundary + '--')
    form.append('')
    body = crlf.join(form)
    return boundary, body


def request_get(path, params, stream=False):
    process = __split_path(path)

    if process['status'] == 'success':
        conn = process['conn']

        # check 2.x and 3.x differences in using urllib
        try:
            conn.request("GET", process['req_path'] + "?" + urllib.urlencode(params))
        except AttributeError:
            conn.request("GET", process['req_path'] + "?" + urllib.parse.urlencode(params))

        resp = conn.getresponse()

        if stream:
            resp_obj = resp
        else:
            assert isinstance(resp, object)
            resp_obj = resp.read()
        return HTTPConnect(resp.status, resp_obj)
    else:
        return HTTPConnect(404, process)


def request_post(path, params, files=None, stream=False):
    process = __split_path(path)

    if process['status'] == 'success':
        conn = process['conn']

        if files:
            boundary, body = __encode_multipart_formdata(params, files)
            header = {'content-type': 'multipart/form-data; boundary=' + boundary}

            conn.request("POST", process['req_path'], body, header)
        else:
            try:
                conn.request("POST", process['req_path'] + "?" + urllib.urlencode(params))
            except AttributeError:
                conn.request("POST", process['req_path'] + "?" + urllib.parse.urlencode(params))

        resp = conn.getresponse()

        if stream:
            resp_obj = resp
        else:
            resp_obj = resp.read()
        return HTTPConnect(resp.status, resp_obj)
    else:
        return HTTPConnect(404, process)
