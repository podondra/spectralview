import tornado.httpclient as httpclient


def request_url(url):
    http_client = httpclient.HTTPClient()   # TODO AsyncHTTPClient
    response = None
    try:
        response = http_client.fetch(url)
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses
        print("Error: " + str(e))   # TODO log
    except Exception as e:
        # other errors are possible such as IOError
        print("Error: " + str(e))   # TODO log
    http_client.close()
    return response
