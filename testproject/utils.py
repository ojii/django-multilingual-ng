from django.test import TestCase
from django.contrib.auth.models import User

class AdminTestCase(TestCase):
    """
    A base class for test cases that need to access the admin
    interface.

    All it does is logging in as a superuser in setUp.
    """
    def setUp(self):
        self.user = User.objects.get_or_create(username='admin',
                                               email='admin@test.elksoft.pl')[0]
        self.user.set_password('admin')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username = 'admin', password = 'admin')

def to_str(arg):
    """
    Convert all unicode strings in a structure into 'str' strings.

    Utility function to make it easier to write tests for both
    unicode and non-unicode Django.
    """
    if type(arg) == list:
        return [to_str(el) for el in arg]
    elif type(arg) == tuple:
        return tuple([to_str(el) for el in arg])
    elif arg is None:
        return None
    else:
        return str(arg)
