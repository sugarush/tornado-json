from pprint import pprint
from unittest import skip

from tornado import testing, web, gen

from tornado_json import JSONHandler


class TestHandler(JSONHandler):

    def get(self):
        self.write(self.encode({
            'success': 'it worked'
        }))
        self.finish()


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
        provider = response.headers.get('X-Provider')
        self.assertEqual(provider, JSONHandler.default_provider)

        self._app.settings.update({'provider': 'application'})

        response = self.fetch('/provider_default',
            method='GET'
        )
        provider = response.headers.get('X-Provider')
        self.assertEqual(provider, 'application')

        response = self.fetch('/provider_handler',
            method='GET'
        )
        provider = response.headers.get('X-Provider')
        self.assertEqual(provider, 'handler')

    @skip('untested')
    def test_initialize_version(self):
        pass

    @skip('untested')
    def test_initialize_origin(self):
        pass

    @skip('untested')
    def test_prepare_uuid_from_client(self):
        pass

    @skip('untested')
    def test_prepare_uuid_from_server(self):
        pass

    @skip('untested')
    def test_get_content_type(self):
        pass

    @skip('untested')
    def test_send_json(self):
        pass

    @skip('untested')
    def test_write_error(self):
        pass

    @skip('untested')
    def test_write_error_with_stack_stack_trace(self):
        pass

    @skip('untested')
    def test_format(self):
        pass

    @skip('untested')
    def test_send_result(self):
        pass
