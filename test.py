import sys

from pprint import pprint
from unittest import skip

from uuid import uuid4

from tornado import testing, web, gen

from tornado_json import JSONHandler


class TestHandler(JSONHandler):

    def get(self):
        self.write(self.encode({
            'success': 'it worked'
        }))
        self.finish()

    def put(self):
        data = self.request.body
        self.send_json(200, data)

    def post(self):
        try:
            raise Exception('Server error')
        except Exception, error:
            self.send_error(500, reason=error.message)

    def delete(self):
        try:
            raise Exception('Server error')
        except Exception, error:
            self.send_error(500,
                reason=error.message,
                exc_info=sys.exc_info(),
            )


class TestJSONHandler(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestJSONHandler, self).setUp()
        self.json_to_encode = { 'alpha': 'a' }
        self.json_to_decode = '{"alpha":"a"}'

    # must be implemented to run tests
    def get_app(self):
        return web.Application()

    def test_encode(self):
        data = JSONHandler.encode(self.json_to_encode)
        self.assertEqual(data, self.json_to_decode)

    def test_decode(self):
        data = JSONHandler.decode(self.json_to_decode)
        self.assertEqual(data, self.json_to_encode)

    def test_initialize_provider(self):
        self._app.add_handlers(r'.*', [
            (r'/provider_default', TestHandler),
            (r'/provider_handler', TestHandler, {'provider': 'handler'}),
        ])

        response = self.fetch('/provider_default',
            method='GET'
        )
        provider = response.headers.get('Provider')
        self.assertEqual(provider, JSONHandler.default_provider)

        self._app.settings.update({'provider': 'application'})

        response = self.fetch('/provider_default',
            method='GET'
        )
        provider = response.headers.get('Provider')
        self.assertEqual(provider, 'application')

        response = self.fetch('/provider_handler',
            method='GET'
        )
        provider = response.headers.get('Provider')
        self.assertEqual(provider, 'handler')

    def test_initialize_version(self):
        self._app.add_handlers(r'.*', [
            (r'/version_default', TestHandler),
            (r'/version_handler', TestHandler, {'version': 'handler'}),
        ])

        response = self.fetch('/version_default',
            method='GET'
        )
        version = response.headers.get('Version')
        self.assertEqual(version, JSONHandler.default_version)

        self._app.settings.update({'version': 'application'})

        response = self.fetch('/version_default',
            method='GET'
        )
        version = response.headers.get('Version')
        self.assertEqual(version, 'application')

        response = self.fetch('/version_handler',
            method='GET'
        )
        version = response.headers.get('Version')
        self.assertEqual(version, 'handler')

    def test_initialize_origin(self):
        self._app.add_handlers(r'.*', [
            (r'/origin_default', TestHandler),
            (r'/origin_handler', TestHandler, {'origin': 'handler'}),
        ])

        response = self.fetch('/origin_default',
            method='GET'
        )
        origin = response.headers.get('Origin')
        self.assertEqual(origin, JSONHandler.default_origin)

        self._app.settings.update({'origin': 'application'})

        response = self.fetch('/origin_default',
            method='GET'
        )
        origin = response.headers.get('Origin')
        self.assertEqual(origin, 'application')

        response = self.fetch('/origin_handler',
            method='GET'
        )
        origin = response.headers.get('Origin')
        self.assertEqual(origin, 'handler')

    def test_prepare_uuid_from_client(self):
        self._app.add_handlers(r'.*', [
            (r'/uuid', TestHandler),
        ])

        uuid = str(uuid4())

        response = self.fetch('/uuid',
            method='GET',
            headers={
                'Request-Id': uuid,
            }
        )

        self.assertEqual(response.headers['Request-Id'], uuid)

    def test_prepare_uuid_from_server(self):
        self._app.add_handlers(r'.*', [
            (r'/uuid', TestHandler),
        ])

        response = self.fetch('/uuid',
            method='GET',
        )

        self.assertIsNotNone(response.headers['Request-Id'])

    def test_prepare_uuid_invalid(self):
        self._app.add_handlers(r'.*', [
            (r'/uuid', TestHandler),
        ])

        uuid = 'invalid'

        response = self.fetch('/uuid',
            method='GET',
            headers={
                'Request-Id': uuid,
            }
        )

        self.assertIsNotNone(response.headers['Request-Id'])
        self.assertNotEqual(response.headers['Request-Id'], uuid)

    def test_content_type(self):
        self._app.add_handlers(r'.*', [
            (r'/content_type', TestHandler),
        ])

        response = self.fetch('/content_type',
            method='GET',
        )

        content_type = 'application/unknown.api+json; version=unknown'
        self.assertEqual(response.headers['Content-Type'], content_type)

    def test_send_json(self):
        self._app.add_handlers(r'.*', [
            (r'/send_json', TestHandler),
        ])

        data = JSONHandler.encode({
            'send_json': 'test'
        })


        response = self.fetch('/send_json',
            method='PUT',
            body=data,
        )

        self.assertEqual(data, JSONHandler.decode(response.body))

    def test_write_error(self):
        self._app.add_handlers(r'.*', [
            (r'/write_error', TestHandler),
        ])

        response = self.fetch('/write_error',
            method='POST',
            body='empty'
        )

        error = '{"error":"Server error"}'
        self.assertEqual(response.body, error)

    def test_write_error_with_stack_stack_trace(self):
        self._app.add_handlers(r'.*', [
            (r'/write_error', TestHandler),
        ])

        response = self.fetch('/write_error',
            method='DELETE'
        )

        error = '{"error":"Server error"}'
        self.assertEqual(response.body, error)
