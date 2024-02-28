from django.contrib.auth import get_user_model
from django.test import Client

from manager.models import Company, Offer, RecruitmentStep, StepType

User = get_user_model()


class TestingBase:
    def setUp(self):
        self.client = Client()

        self.password = "VeryLongAndS3CUREPa$$word!23"
        self.user = User.objects.create_user(username="test_user", email="test@dev.dev", password=self.password)
        self.company = Company.objects.create(name="Test company", added_by=self.user)
        self.offer = Offer.objects.create(title="Test Offer", developer=self.user, company=self.company)
        self.step = RecruitmentStep.objects.create(offer=self.offer)

        self.password2 = "OtherLongAndS3CUREPa$$word!@"
        self.other_user = User.objects.create_user(username="user2", email="t35t@dev.dev", password=self.password2)

        self.step_type = StepType.objects.create(name="Test type", added_by=self.user)

    def log_user(self, email=None, password=None):
        user_is_logged = self.client.login(
            username=email or self.user.email,
            password=password or self.password,
        )
        self.assertTrue(user_is_logged)
