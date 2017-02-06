import json, re

from uuid import uuid4

from tornado.web import RequestHandler
from tornado.escape import to_basestring


UUID_REGEX = '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'

def encode(data):
    return json.dumps(data, separators=(',',':')).replace("</", "<\\/")

def decode(data):
    return json.loads(to_basestring(data))


class JSONHandler(RequestHandler):

    def initialize(self, provider=None, version=None, origin=None):
        self.provider = provider or self.settings.get('provider', 'unknown')
        self.version = version or self.settings.get('version', 'unknown')
        self.origin = origin or self.settings.get('origin', '*')
        self.valid_uuid = re.compile(UUID_REGEX)
        self.uuid = None

    def prepare(self):
        uuid = self.request.headers.get('Request-Id')
        if not uuid or not self.valid_uuid.match(uuid):
            uuid = str(uuid4())
            self.request.headers['Request-Id'] = uuid
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', self.get_content_type())
        self.set_header('Request-Id', uuid)
        self.uuid = uuid

    def get_content_type(self):
        return 'application/api.{provider}+json; version={version}'.format(
            provider=self.provider,
            version=self.version
        )

    def send_json(self, status, data):
        self.set_status(status)
        self.write(encode(data))
        self.finish()

    # called by send_error
    def write_error(self, status, **kargs):
        # set_status has already been called in send_error
        self.write(encode({ 'error': kargs.get('reason') }))
        self.finish()

    def format(self, item):
        item['_id'] = str(item['_id'])
        return item

    def send_result(self, data=None, status=None):
        if data:
            self.send_json(status or 200, map(self.format, data))
        else:
            self.send_error(status or 204, reason='resource not found')