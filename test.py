from pprint import pprint
from unittest import skip

from tornado import testing, web, gen

from tornado_json import JSONHandler


class TestHandler(JSONHandler):

    def get(self):
        pass


def get_app(**kargs):
    return web.Application([
        (r'/json', TestHandler)
    ], **kargs)


class TestJSONHandler(testing.AsyncHTTPTestCase):

    def setUp(self):
        super(TestJSONHandler, self).setUp()
        self.json_to_encode = { 'alpha': 'a' }
        self.json_to_decode = '{"alpha":"a"}'

    # must be implemented to run tests
    def get_app(self):
        pass

    def test_encode(self):
        data = JSONHandler.encode(self.json_to_encode)
        self.assertEqual(data, self.json_to_decode)

    def test_decode(self):
        data = JSONHandler.decode(self.json_to_decode)
        self.assertEqual(data, self.json_to_encode)

    @skip('untested')
    def test_initialize_provider(self):
        pass

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
    def test_write_error_with_stack_stack_trace(self):
        pass

    @skip('untested')
    def test_format(self):
        pass

    @skip('untested')
    def test_send_result(self):
        pass
