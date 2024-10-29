from django.test import TestCase
from rest_framework.test import APIClient
from .models import User, Role
from .services import AuthService, UserService


# Create your tests here.
class UserAPITestCase(TestCase):
    def setUp(self):
        user_service = UserService()
        auth_service = AuthService()
        self.client = APIClient()
        self.role = Role.objects.create(name="test")
        self.user = user_service.create_user(
            email="test@test.com", password="testpass", role=self.role
        )
        self.token = auth_service.generate_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token["access"]}")

    def test_register_user(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Testing",
                "last_name": "Testing",
                "email": "testing@test.com",
                "password": "test123",
                "role_id": self.role.id,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 4)

    def test_register_user_when_not_provide_auth_jwt(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Testing",
                "last_name": "Testing",
                "email": "testing@test.com",
                "password": "test123",
                "role_id": self.role.id,
            },
            headers=None,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 4)

    def test_fail_register_user_when_not_exist_role(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "first_name": "Testing",
                "last_name": "Testing",
                "email": "testing@test.com",
                "password": "test123",
                "role_id": 2220,
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_sign_in(self):
        response = self.client.post(
            "/api/v1/auth/sign_in/",
            {
                "email": self.user.email,
                "password": "testpass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_fail_login_with_fail_credentials(self):
        response = self.client.post(
            "/api/v1/auth/sign_in/",
            {
                "email": self.user.email,
                "password": "incorrect_password",
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(len(response.data), 4)
