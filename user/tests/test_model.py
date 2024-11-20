import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'instagram_api.settings'
from django.test import TransactionTestCase
from user.models import User

class MyModelTransactionTest(TransactionTestCase):
    databases = {'default', 'test'}

    def test_create_object(self):
        obj = User.objects.create(username="Test Object",password='Bhole@057p',email="bhole@gmail.com")
        self.assertEqual(User.objects.count(), 1)



    # def test_cleanup(self):
    #     # You can manually clean up if needed
    #     User.objects.all().delete()
    #     self.assertEqual(User.objects.count(), 0)

    
