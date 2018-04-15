from tornado.log import access_log

def log(handler):
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()
    log_method("%s %s %s %d %s %.2fms", handler.uuid, handler.request.method, handler.request.uri, handler.get_status(), handler._reason, request_time)
