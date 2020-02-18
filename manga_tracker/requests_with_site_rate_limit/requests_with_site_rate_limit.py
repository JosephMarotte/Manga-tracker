import requests
import bisect
from time import time

# TODO improve this file overall and puts it in its own repository


# TODO try to improve this to return a real requests.Response
class FakeResponse:
    status_code = 429

    def __init__(self, waiting_time):
        self.time_to_wait = waiting_time


def simplify_rate_limit_list(rate_limit_list):
    rate_limit_list.sort(key=lambda tup: tup[0])
    rate_limit_list.sort(key=lambda tup: tup[0] / tup[1])

    new_list = [rate_limit_list[0]]
    for i in range(1, len(rate_limit_list)):
        if rate_limit_list[i][0] < new_list[-1][0]:
            new_list.append(rate_limit_list[i])
    new_list.sort(key=lambda tup: tup[0], reverse=True)
    return new_list


class _SetRateLimit:
    class __SetRateLimit:
        def __init__(self):
            self.website_to_site_rate_limit = {}
            self.website_to_site_rate_limit_history = {}

    instance = None

    def __init__(self, func, site_rate_limit_list, website_name):
        if not self.instance:
            self.instance = self.__SetRateLimit()
        self.func = func
        if website_name in self.instance.website_to_site_rate_limit:
            self.instance.website_to_site_rate_limit[website_name] += site_rate_limit_list
        else:
            self.instance.website_to_site_rate_limit[website_name] = site_rate_limit_list
            self.instance.website_to_site_rate_limit_history[website_name] = []  # empty history for this website
        self.instance.website_to_site_rate_limit[website_name] = simplify_rate_limit_list(self.instance.website_to_site_rate_limit[website_name])

    def __call__(self, *args, **kwargs):
        website = args[0].split("/")[2]
        if website not in self.instance.website_to_site_rate_limit:
            return self.func(*args, **kwargs)

        current_time = time()

        # remove unneeded elements
        max_over_time = self.instance.website_to_site_rate_limit[website][0][1]
        min_min_threshold = current_time - max_over_time
        index_min_min_threshold = bisect.bisect(self.instance.website_to_site_rate_limit_history[website], min_min_threshold)
        self.instance.website_to_site_rate_limit_history[website] = self.instance.website_to_site_rate_limit_history[website][index_min_min_threshold:]

        # check if all the rate limit condition are respected
        time_to_wait = 0
        for nb_request, over_time in self.instance.website_to_site_rate_limit[website]:
            if len(self.instance.website_to_site_rate_limit_history[website]) >= nb_request:
                min_threshold_time = current_time - over_time
                if self.instance.website_to_site_rate_limit_history[website][-nb_request] >= min_threshold_time:
                    time_to_wait = max(time_to_wait, self.instance.website_to_site_rate_limit_history[website][nb_request - 1] - min_threshold_time)

        if time_to_wait == 0:
            res = self.func(*args, **kwargs)
            self.instance.website_to_site_rate_limit_history[website].append(time())
            return res
        else:
            return FakeResponse(time_to_wait)


def set_rate_limit(function=None, site_rate_limit_list=[(600, 600)], website_name="dummy_name"): #  by default 600 requests / 600 secs
    if function:
        return _SetRateLimit(function, site_rate_limit_list, website_name)
    else:
        def wrapper(f):
            return _SetRateLimit(f, site_rate_limit_list, website_name)
        return wrapper


def decorate_get_request(rate, website):
    obj = getattr(requests, 'get')
    setattr(requests, 'get', set_rate_limit(obj, rate, website))
