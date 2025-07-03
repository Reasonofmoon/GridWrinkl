# -*- coding: utf-8 -*-

import unittest
import sys
import os

# Add src to the Python path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from user_authentication import services
from user_authentication.models import User

class TestUserAuthentication(unittest.TestCase):
    """
    user_authentication 서비스에 대한 테스트 케이스
    """

    def setUp(self):
        """
        각 테스트 전에 실행되는 설정 메서드
        - 사용자 데이터베이스를 초기화합니다.
        """
        services._users_db.clear()

    def test_create_user_success(self):
        """
        사용자 생성 성공 테스트
        """
        user = services.create_user("testuser", "test@example.com", "password123")
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertIn(user.id, services._users_db)

    def test_create_user_duplicate_email(self):
        """
        중복된 이메일로 사용자 생성 시도 시 실패 테스트
        """
        services.create_user("user1", "test@example.com", "pass1")
        with self.assertRaises(ValueError):
            services.create_user("user2", "test@example.com", "pass2")

    def test_get_user_by_email_found(self):
        """
        이메일로 사용자 찾기 성공 테스트
        """
        created_user = services.create_user("testuser", "test@example.com", "password123")
        found_user = services.get_user_by_email("test@example.com")
        self.assertIsNotNone(found_user)
        self.assertEqual(created_user.id, found_user.id)

    def test_get_user_by_email_not_found(self):
        """
        존재하지 않는 이메일로 사용자 찾기 실패 테스트
        """
        found_user = services.get_user_by_email("nonexistent@example.com")
        self.assertIsNone(found_user)

    def test_verify_password_correct(self):
        """
        올바른 비밀번호 검증 테스트
        """
        user = services.create_user("testuser", "test@example.com", "password123")
        self.assertTrue(services.verify_password("password123", user.hashed_password))

    def test_verify_password_incorrect(self):
        """
        틀린 비밀번호 검증 테스트
        """
        user = services.create_user("testuser", "test@example.com", "password123")
        self.assertFalse(services.verify_password("wrongpassword", user.hashed_password))

if __name__ == '__main__':
    unittest.main()
