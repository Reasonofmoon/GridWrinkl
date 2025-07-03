# -*- coding: utf-8 -*-

from user_authentication import services

def main():
    """
    메인 함수: 사용자 생성 및 로그인 시뮬레이션
    """
    print("--- 사용자 생성 ---")
    try:
        user1 = services.create_user("testuser", "test@example.com", "password123")
        print(f"사용자 '{user1.username}' 생성 성공!")
        print(f"이메일: {user1.email}")
    except ValueError as e:
        print(f"오류: {e}")

    print("\n--- 중복 사용자 생성 시도 ---")
    try:
        services.create_user("anotheruser", "test@example.com", "password456")
    except ValueError as e:
        print(f"예상된 오류 발생: {e}")

    print("\n--- 로그인 시뮬레이션 ---")
    email_to_check = "test@example.com"
    password_to_check = "password123"
    
    user_to_login = services.get_user_by_email(email_to_check)
    
    if user_to_login:
        print(f"'{email_to_check}' 사용자를 찾았습니다.")
        if services.verify_password(password_to_check, user_to_login.hashed_password):
            print("로그인 성공!")
        else:
            print("로그인 실패: 비밀번호가 일치하지 않습니다.")
    else:
        print(f"'{email_to_check}' 사용자를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
