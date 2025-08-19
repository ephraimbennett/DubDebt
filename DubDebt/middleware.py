# project/middleware.py
class HostSwitchURLConf:
    TARGET_HOSTS = {"secure.dubdebt.com"}  # add more if needed

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        if host in self.TARGET_HOSTS:
            request.urlconf = "DubDebt.collect_urls"  # debtor at '/'
        return self.get_response(request)
