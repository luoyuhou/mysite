from django.test import TestCase

# Create your tests here.


class People(object):
    name = None
    age = None



def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    return pr

p = People()
p = props(p)
print(type(p), p)


d = {}
d[1] = 'abc'
d[2] = 'qwe'
print('d', type(d), d)
for i in d:
    print('i', type(i), i, d[i])


a = None
if a:
    print(123)
else:
    print(345)

l = [1, 2, 3, 4]
l.remove(2)
print(l)
