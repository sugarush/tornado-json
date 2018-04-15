import json, re, traceback

from uuid import uuid4

from tornado.web import RequestHandler
from tornado.escape import to_basestring
from tornado.log import access_log


class JSONHandler(RequestHandler):

    UUID_REGEX = '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'

    default_provider = 'unknown'
    default_version  = 'unknown'
    default_origin   = '*'

    @classmethod
    def encode(cls, data):
        return json.dumps(data, separators=(',',':')).replace("</", "<\\/")

    @classmethod
    def decode(cls, data):
        return json.loads(to_basestring(data))

    def initialize(self, **kargs):
        self.provider = kargs.get('provider') or self.settings.get(
            'provider', self.default_provider
        )
        self.version = kargs.get('version') or self.settings.get(
            'version', self.default_version
        )
        self.origin = kargs.get('origin') or self.settings.get(
            'origin', self.default_origin
        )
        self.valid_uuid = re.compile(self.UUID_REGEX)
        self.uuid = None

    def prepare(self):
        uuid = self.request.headers.get('Request-Id')
        if not uuid or not self.valid_uuid.match(uuid):
            uuid = str(uuid4())
            self.request.headers['Request-Id'] = uuid
        self.set_header('Access-Control-Allow-Origin', self.origin)
        self.set_header('Content-Type', self.content_type())
        self.set_header('Provider', self.provider)
        self.set_header('Version', self.version)
        self.set_header('Origin', self.origin)
        self.set_header('Request-Id', uuid)
        self.uuid = uuid
        try:
            self.body = self.decode(self.request.body or '{ }')
        except Exception as error:
            self.send_error(400, reason='json decode error: %s' % str(error))

    def content_type(self):
        return 'application/{provider}.api+json; version={version}'.format(
            provider=self.provider,
            version=self.version
        )

    def send_json(self, status, data):
        self.set_status(status)
        self.write(self.encode(data))
        self.finish()

    # called by `send_error` in RequestHandler
    def clear(self):
        # don't reset the headers
        self._write_buffer = []
        self._status_code = 200
        self._reason = httputil.responses[200]

    # called by `send_error` in RequestHandler
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
