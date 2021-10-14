class HttpResponse(object):
    def __init__(self, something, other):
        self.something = something
        self.other = other


def example(func):
    def wrapper(request, *args, **kwargs):
        print('Started')
        print(request.something)
        func(request, *args, **kwargs)
        print("End")
        print(args)
        print(kwargs)
    return wrapper


@example
def f(request: HttpResponse, s):
    print(s)


request = HttpResponse("smth", "other")
f(request, "carlos")
