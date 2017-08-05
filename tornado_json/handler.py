import json, re, traceback

from uuid import uuid4

from tornado.web import RequestHandler
from tornado.escape import to_basestring
from tornado.log import access_log


class JSONHandler(RequestHandler):

    UUID_REGEX = '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'

    @classmethod
    def encode(cls, data):
        return json.dumps(data, separators=(',',':')).replace("</", "<\\/")

    @classmethod
    def decode(cls, data):
        return json.loads(to_basestring(data))

    def initialize(self, provider=None, version=None, origin=None):
        self.provider = provider or self.settings.get('provider', 'unknown')
        self.version = version or self.settings.get('version', 'unknown')
        self.origin = origin or self.settings.get('origin', '*')
        self.valid_uuid = re.compile(self.UUID_REGEX)
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
        self.write(self.encode(data))
        self.finish()

    # called by send_error
    def write_error(self, status, **kargs):
        # set_status has already been called in send_error
        if 'exc_info' in kargs:
            stack_trace = traceback.format_exception(*kargs['exc_info'])
            stack_trace = str.join('', stack_trace).rstrip('\n')
            stack_trace = ('%s\n%s' % (self.uuid, stack_trace))
            if status >= 500:
                access_log.error(stack_trace)
            elif status >= 400:
                access_log.warning(stack_trace)
            elif status >= 200:
                access_log.info(stack_trace)
        self.write(self.encode({ 'error': kargs.get('reason') }))
        self.finish()

    def format(self, item):
        item['_id'] = str(item['_id'])
        return item

    def send_result(self, data=None, status=None):
        if data:
            self.send_json(status or 200, map(self.format, data))
        else:
            self.send_error(status or 204, reason='resource not found')
