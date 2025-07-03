# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import uuid

@dataclass
class User:
    """
    사용자 정보를 나타내는 데이터 클래스
    """
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
