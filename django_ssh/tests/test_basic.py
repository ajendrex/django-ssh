# Copyright 2014 Jon Eyolfson
#
# This file is part of Django SSH.
#
# Django SSH is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Django SSH is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Django SSH. If not, see <http://www.gnu.org/licenses/>.

from tempfile import NamedTemporaryFile

from django.contrib.auth.models import User
from django.test import TestCase

class BasicTestCase(TestCase):

    def setUp(self):
        self.u1 = User.objects.create_user('u1', password='p1')
        self.u2 = User.objects.create_user('u2', password='p2')
        self.k1 = {'format': 'ssh-rsa',
                   'data': ('AAAAB3NzaC1yc2EAAAADAQABAAABAQDHmrZYaqcFtZhbvYVINL'
                            'VbWVI8ig4mLqYdzCDIC7uAlnFdOAMsEuSK0zW0CrRQ+19TAPNa'
                            'sm284hqXD7N+nylb8y75BWiUhxh+IK68oxexXdAwpQEKg7pX7P'
                            'B+GuYF7z6zqsubDsOxL3jx/pZNTYfNXTuzYfrfhw83lXxRml75'
                            'x789pFjg9D0D/Bc/yB6sfd8kvFu+vkt/TXmcsvzBtw7AA3J58E'
                            'Iy9nuxon7aDdnwTVkS7DLhBLU/UWXMlkxHHEAL1E+6uxvyCfIN'
                            'rI15kkaiY68/46NWrXSHPmHouBoZnQxYMEkmAd12OMIkilAsS6'
                            'LxGoAB4ABOuQWQepT3kayn'),
                   'fingerprint':
                       'c6:35:81:1c:a3:ed:9b:2b:36:9f:04:27:13:05:85:10'}

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.login(username='u1', password='p1'))
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_add_text_basic(self):
        body = '{format} {data}'.format(**self.k1)
        comment = 'u1 k1'
        fingerprint = self.k1['fingerprint']
        self.assertTrue(self.client.login(username='u1', password='p1'))
        response = self.client.post('/add-text/', {'body': body,
                                                   'comment': comment})
        self.assertRedirects(response, '/')
        self.assertEquals(self.u1.ssh_keys.count(), 1)
        self.assertEquals(self.u1.ssh_keys.get().fingerprint, fingerprint)

    def test_add_text_body_with_comment(self):
        body = '{format} {data} u1 k1'.format(**self.k1)
        self.assertTrue(self.client.login(username='u1', password='p1'))
        response = self.client.post('/add-text/', {'body': body})
        self.assertRedirects(response, '/')
        self.assertEquals(self.u1.ssh_keys.count(), 1)
        self.assertEquals(self.u1.ssh_keys.get().comment, 'u1 k1')

    def test_add_file_valid(self):
        contents = ('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCz5qmlFdgVv5waCl9Xqr'
                    'RLBpkfv/G8mTveYNhaLrLy34NreDSMPqK0qsX4qAn7gl+Aixvj9F4LONid'
                    'xpwrG+gaMVKQ7yHS9oiqQk6YXYmQMI0Pe4dB6kEj3bDgThxNh8D2kgD6CE'
                    'HROzkeXhsj3Z3e3vCqulzhmgYHHesKKnVQKrt38/WTEeeoYKfQGRgZRjUH'
                    'urQlDZN0y65Ohh5zyH1jtQ4TMFUwtWsmKZZVVhA1HnsWF8mcSUoRhaOECH'
                    'reMy9f8qNXsZypM6032rM5GMBsrRv3JT/77kGnHSM1GIPN7rwIeXgDttff'
                    'WMIrjiodT7j7gq1ZON93RBeu5QGgzHo9 u1 k2')
        fingerprint = '51:ca:91:01:0f:14:7b:1a:d9:81:28:d7:9b:46:bb:2a'
        self.assertTrue(self.client.login(username='u1', password='p1'))
        with NamedTemporaryFile('bw+') as f:
            f.write(contents.encode())
            f.flush()
            f.seek(0)
            response = self.client.post('/add-file/', {'file': f})
        self.assertRedirects(response, '/')
        self.assertEquals(self.u1.ssh_keys.count(), 1)
        self.assertEquals(self.u1.ssh_keys.all()[0].fingerprint, fingerprint)

    def test_add_text_invalid(self):
        self.assertTrue(self.client.login(username='u1', password='p1'))
        response = self.client.post('/add-text/', {'body': ''})
        self.assertFormError(response, 'form', 'body', 'This field is required.')
        response = self.client.post('/add-text/', {'body': 'INVALID'})
        self.assertFormError(response, 'form', None, 'Invalid OpenSSH key.')
