# GridWrinkl - 개발 생산성 시스템

GridWrinkl은 물리적 파일 정리 시스템(GridFile)과 AI 맥락 관리 시스템(Wrinkl)을 결합한 하이브리드 개발 생산성 도구입니다. 이 프로젝트는 시각적 그리드를 통해 파일을 직관적으로 관리하고, 체계적인 맥락 관리를 통해 AI 개발 도구와의 연동을 극대화하는 것을 목표로 합니다.

## 🚀 시작하기

### 1. 필요 조건
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2. 설치
이 프로젝트는 별도의 외부 라이브러리 설치가 필요하지만, Flask는 웹 UI를 위해 설치해야 합니다.

```bash
# Flask 웹 프레임워크 설치
pip install Flask
```

### 3. 프로젝트 초기화
`gridwrinkl_cli.py` 스크립트를 사용하여 프로젝트를 초기화할 수 있습니다. 하지만 현재 프로젝트는 이미 초기화되어 있으므로 이 단계를 건너뛸 수 있습니다.

## 🛠️ 사용법

### 1. GridWrinkl CLI (`gridwrinkl_cli.py`)
이 프로젝트의 핵심 관리 도구입니다.

- **프로젝트 초기화**:
  ```bash
  python gridwrinkl_cli.py init "프로젝트 이름"
  ```

- **새 기능 생성**:
  ```bash
  python gridwrinkl_cli.py feature create [기능_이름] --description "[기능_설명]"
  ```

- **기능 목록 조회**:
  ```bash
  python gridwrinkl_cli.py feature list
  ```

- **그리드 재구성**:
  ```bash
  python gridwrinkl_cli.py grid reorganize
  ```

### 2. 웹 애플리케이션 실행
이 프로젝트에는 사용자 인증 및 GridFile 시각화 대시보드를 포함한 웹 UI가 포함되어 있습니다.

1.  **웹 서버 시작**:
    ```bash
    python src/app.py
    ```

2.  **웹 브라우저 접속**:
    - 서버가 시작되면 웹 브라우저를 열고 `http://127.0.0.1:5000`으로 접속합니다.
    - 또는 `http://127.0.0.1:5000/grid`로 바로 접속하여 GridFile 대시보드를 확인할 수 있습니다.

### 3. 테스트 실행
프로젝트의 기능이 올바르게 작동하는지 확인하기 위해 단위 테스트를 실행할 수 있습니다.

```bash
python tests/test_user_authentication.py
```

## 📐 시스템 구조

- **`gridwrinkl_cli.py`**: 프로젝트 관리 및 자동화를 위한 메인 CLI 도구입니다.
- **`src/`**: 웹 애플리케이션의 소스 코드가 위치합니다.
  - **`app.py`**: Flask 웹 서버의 메인 파일입니다.
  - **`main.py`**: CLI 기반의 기능 테스트 스크립트입니다.
  - **`user_authentication/`**: 사용자 인증 기능 관련 모듈입니다.
    - `models.py`: 사용자 데이터 모델 정의.
    - `services.py`: 인증 관련 비즈니스 로직.
  - **`templates/`**: 웹 UI를 위한 HTML 템플릿 파일들이 있습니다.
- **`tests/`**: 단위 테스트 코드가 위치합니다.
- **`.gridfile/`**: GridFile 시스템의 설정 및 레이아웃 데이터가 저장됩니다.
- **`.ai/`**: Wrinkl 시스템의 AI 맥락 데이터가 저장됩니다.
