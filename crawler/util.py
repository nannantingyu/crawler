def get_url_param(url):
    if "?" not in url:
        return None

    url = url.split("?")[-1]
    params = {}
    for param in url.split("&"):
        pa = param.split("=")
        params[pa[0]] = pa[1]

    return params