# 개발 패턴 및 가이드라인

## 코딩 스타일
```python
# 함수명: snake_case
def process_user_data(user_input: str) -> Dict:
    pass

# 클래스명: PascalCase  
class UserDataProcessor:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
```

## 금기 패턴 
❌ 전역 변수 남용
❌ 매직 넘버 사용
❌ 과도한 중첩 (3단계 이상)
❌ 함수 당 50줄 이상

## 테스트 전략
- **단위 테스트**: 모든 함수 85% 이상 커버리지
- **통합 테스트**: 주요 워크플로우 커버
- **E2E 테스트**: 핵심 사용자 시나리오

## GridFile 연동 패턴
- **활성 개발 파일**: 빨간색 블록 (active 존)
- **참조 자료**: 파란색 블록 (resources 존)
- **완료 파일**: 초록색 블록 (archive 존)

## 파일 명명 규칙
- **기능별**: `feature_name_component.ext`
- **유틸리티**: `utils_specific_purpose.ext`
- **테스트**: `test_feature_name.ext`
- **문서**: `docs_topic_name.md`
