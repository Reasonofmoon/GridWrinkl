# -*- coding: utf-8 -*-

from typing import Dict, Optional
from .models import User

# 데이터베이스를 흉내 내기 위한 임시 저장소
_users_db: Dict[str, User] = {}

# 비밀번호 해싱을 위한 간단한 모의 함수
# 실제 애플리케이션에서는 bcrypt나 argon2와 같은 강력한 라이브러리를 사용해야 합니다.
def _hash_password(password: str) -> str:
    """간단한 비밀번호 해싱 흉내"""
    return f"hashed_{password}"

def create_user(username: str, email: str, password: str) -> User:
    """
    새로운 사용자를 생성하고 데이터베이스에 추가합니다.

    Args:
        username: 사용자 이름
        email: 사용자 이메일
        password: 사용자 비밀번호

    Returns:
        생성된 User 객체
    """
    if email in [user.email for user in _users_db.values()]:
        raise ValueError("이미 사용 중인 이메일입니다.")

    hashed_password = _hash_password(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    _users_db[new_user.id] = new_user
    return new_user

def get_user_by_email(email: str) -> Optional[User]:
    """
    이메일로 사용자를 찾습니다.

    Args:
        email: 찾을 사용자의 이메일

    Returns:
        찾은 User 객체 또는 None
    """
    for user in _users_db.values():
        if user.email == email:
            return user
    return None

def verify_password(password: str, hashed_password: str) -> bool:
    """
    비밀번호가 해시와 일치하는지 확인합니다.

    Args:
        password: 확인할 비밀번호
        hashed_password: 저장된 해시된 비밀번호

    Returns:
        비밀번호 일치 여부
    """
    return _hash_password(password) == hashed_password
