
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GridWrinkl CLI: GridFile과 Wrinkl 시스템을 통합한 개발 생산성 도구

이 도구는 다음 기능을 제공합니다:
- 프로젝트 초기화 및 구성
- 기능 원장(ledger) 관리
- GridFile 레이아웃 관리
- AI 도구 설정 자동화
- 맥락 동기화 및 최적화
"""

import os
import sys
import json
import yaml
import shutil
import datetime
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


class ConsoleColors:
    """콘솔 색상 코드"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GridWrinkl:
    """
    GridWrinkl 시스템 핵심 클래스
    
    GridFile과 Wrinkl 시스템을 통합하여 파일 정리와 AI 맥락 관리를 
    함께 처리하는 하이브리드 시스템입니다.
    """
    
    def __init__(self, project_path: str = ".", debug: bool = False):
        """
        GridWrinkl 인스턴스 초기화
        
        Args:
            project_path: 프로젝트 경로 (기본값: 현재 디렉토리)
            debug: 디버그 모드 활성화 여부
        """
        self.project_path = Path(project_path).resolve()
        self.debug_mode = debug
        self.gridfile_dir = self.project_path / ".gridfile"
        self.ai_dir = self.project_path / ".ai"
        self.config = None
        
        # 색상 관련 선호도
        self.color_enabled = True
        
        # 영역 매핑 (카테고리 -> 그리드 영역)
        self.category_to_zone = {
            "active": "active",
            "pending": "active",
            "archive": "archive",
            "completed": "archive",
            "resources": "resources",
            "reference": "resources"
        }
        
        # AI 도구 설정 파일 매핑
        self.ai_tools = {
            "cursor": ".cursorrules",
            "copilot": ".github/copilot-instructions.md",
            "windsurf": ".windsurfrules",
            "augment": "augment.md"
        }
        
    def _log_debug(self, message: str) -> None:
        """디버그 메시지 출력"""
        if self.debug_mode:
            print(f"{ConsoleColors.CYAN}[DEBUG] {message}{ConsoleColors.ENDC}")
    
    def _log_info(self, message: str) -> None:
        """정보 메시지 출력"""
        if self.color_enabled:
            print(f"{ConsoleColors.BLUE}[INFO] {message}{ConsoleColors.ENDC}")
        else:
            print(f"[INFO] {message}")
    
    def _log_success(self, message: str) -> None:
        """성공 메시지 출력"""
        if self.color_enabled:
            print(f"{ConsoleColors.GREEN}[SUCCESS] {message}{ConsoleColors.ENDC}")
        else:
            print(f"[SUCCESS] {message}")
    
    def _log_warning(self, message: str) -> None:
        """경고 메시지 출력"""
        if self.color_enabled:
            print(f"{ConsoleColors.YELLOW}[WARNING] {message}{ConsoleColors.ENDC}")
        else:
            print(f"[WARNING] {message}")
    
    def _log_error(self, message: str) -> None:
        """에러 메시지 출력"""
        if self.color_enabled:
            print(f"{ConsoleColors.RED}[ERROR] {message}{ConsoleColors.ENDC}")
        else:
            print(f"[ERROR] {message}")
    
    def is_initialized(self) -> bool:
        """
        프로젝트가 이미 GridWrinkl로 초기화되었는지 확인
        
        Returns:
            bool: 초기화 여부
        """
        return (self.gridfile_dir.exists() and 
                self.ai_dir.exists() and 
                (self.gridfile_dir / "config.json").exists())
    
    def init(self, project_name: str, force: bool = False) -> bool:
        """
        프로젝트 초기화
        
        Args:
            project_name: 프로젝트 이름
            force: 기존 구성이 있을 경우 강제 덮어쓰기
            
        Returns:
            bool: 초기화 성공 여부
        """
        if self.is_initialized() and not force:
            self._log_warning("이미 GridWrinkl로 초기화된 프로젝트입니다.")
            self._log_warning("기존 설정을 덮어쓰려면 --force 옵션을 사용하세요.")
            return False
        
        self._log_info(f"프로젝트 '{project_name}'을(를) 초기화합니다...")
        
        # 1. 기본 디렉토리 구조 생성
        self._create_directory_structure()
        
        # 2. 기본 설정 파일 생성
        self._create_config(project_name)
        
        # 3. 맥락 파일 생성
        self._create_context_files(project_name)
        
        # 4. AI 도구 설정 생성
        self._create_ai_tool_configs(project_name)
        
        # 5. 프로젝트 파일 스캔 및 분석
        self._scan_and_organize_files()
        
        self._log_success(f"프로젝트 '{project_name}'이(가) 성공적으로 초기화되었습니다!")
        self._log_info("다음 단계: 'gridwrinkl feature <feature-name>'으로 첫 기능을 시작하세요.")
        
        return True
    
    def _create_directory_structure(self) -> None:
        """기본 디렉토리 구조 생성"""
        self._log_info("기본 디렉토리 구조를 생성합니다...")
        
        directories = [
            ".gridfile",
            ".gridfile/layouts",
            ".gridfile/templates",
            ".gridfile/backups",
            ".ai",
            ".ai/ledgers",
            ".ai/ledgers/active",
            ".ai/ledgers/archived",
            ".ai/templates",
            ".ai/resources",
            ".ai/patterns",
            ".ai/context-snapshots"
        ]
        
        for directory in directories:
            dir_path = self.project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self._log_debug(f"디렉토리 생성: {dir_path}")
    
    def _create_config(self, project_name: str) -> None:
        """기본 설정 파일 생성"""
        config = {
            "project_name": project_name,
            "version": "1.0.0",
            "created_at": datetime.datetime.now().isoformat(),
            "grid_size": {"width": 12, "height": 8},
            "zones": {
                "active": {"x": 0, "y": 0, "width": 6, "height": 4},
                "resources": {"x": 6, "y": 0, "width": 6, "height": 4},
                "archive": {"x": 0, "y": 4, "width": 12, "height": 4}
            },
            "ai_tools": ["cursor", "copilot"],
            "auto_organize": True
        }
        
        config_path = self.gridfile_dir / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self._log_debug(f"설정 파일 생성: {config_path}")
        self.config = config
    
    def _create_context_files(self, project_name: str) -> None:
        """기본 맥락 파일 생성"""
        self._log_info("맥락 파일을 생성합니다...")
        
        # 1. 프로젝트 개요
        project_md = f"""# {project_name}

## 프로젝트 개요
- **생성일**: {datetime.datetime.now().strftime('%Y-%m-%d')}
- **GridFile-Wrinkl 버전**: 1.0.0

## 설명
이 프로젝트는 GridWrinkl 하이브리드 시스템으로 관리됩니다.

## 주요 기능
- TBD

## 기술 스택
- TBD

## 개발 가이드라인
- `.ai/patterns.md` 파일에서 코딩 패턴 확인
- `.ai/architecture.md` 파일에서 아키텍처 가이드 확인
- `.ai/ledgers/` 디렉토리에서 기능별 개발 원장 확인
"""
        
        with open(self.ai_dir / "project.md", "w", encoding="utf-8") as f:
            f.write(project_md)
        
        # 2. 패턴 가이드
        patterns_md = """# 개발 패턴 및 가이드라인

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
"""
        
        with open(self.ai_dir / "patterns.md", "w", encoding="utf-8") as f:
            f.write(patterns_md)
        
        # 3. 아키텍처 가이드
        architecture_md = """# 시스템 아키텍처

## 전체 구조
```
프로젝트
├── 프레젠테이션 레이어
├── 비즈니스 로직 레이어  
├── 데이터 접근 레이어
└── 인프라 레이어
```

## 주요 기술 결정
- TBD

## 보안 고려사항
- 입력 검증 필수
- 인증/인가 체계 구현
- 민감 정보 관리 방안

## 확장성 전략
- 모듈화된 설계
- 명확한 인터페이스 정의
- 의존성 주입 패턴 활용

## GridFile 통합 아키텍처
- **개발 파일**: 활성 존에 배치
- **설정 파일**: 리소스 존에 배치
- **빌드 결과물**: 아카이브 존에 배치
"""
        
        with open(self.ai_dir / "architecture.md", "w", encoding="utf-8") as f:
            f.write(architecture_md)
        
        # 4. AI 컨텍스트 규칙
        context_rules_md = """# AI 어시스턴트 가이드라인

## 기본 원칙
1. **맥락 우선**: 항상 .ai/ 디렉토리의 정보를 먼저 확인
2. **일관성**: patterns.md의 가이드라인 준수
3. **점진적 개선**: 기존 코드 스타일과 조화
4. **문서화**: 코드 변경 시 관련 문서 업데이트

## 코드 생성 규칙
- 주석은 한국어로 작성
- 함수 docstring은 필수
- 타입 힌트 사용
- 에러 처리 포함

## 파일 구조 규칙
- 새 파일 생성 시 GridFile 블록 생성
- 기능별 디렉토리 구조 유지
- 임시 파일은 .tmp/ 디렉토리에 생성

## 품질 체크리스트
- [ ] 코드 스타일 준수
- [ ] 테스트 코드 포함
- [ ] 문서 업데이트
- [ ] GridFile 블록 할당
- [ ] 보안 검토 완료
"""
        
        with open(self.ai_dir / "context-rules.md", "w", encoding="utf-8") as f:
            f.write(context_rules_md)
        
        # 5. 활성 기능 대시보드
        active_md = f"""# 활성 기능 대시보드

## 현재 개발 중인 기능
*이 파일은 자동 업데이트됩니다*

생성일: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 활성 기능 목록
- 아직 등록된 기능이 없습니다
- `gridwrinkl feature <feature-name>` 명령어로 새 기능을 시작하세요

## GridFile 상태
- **활성 블록**: 0개
- **대기 블록**: 0개  
- **완료 블록**: 0개
- **그리드 효율성**: 0%

## 최근 활동
- {datetime.datetime.now().strftime('%Y-%m-%d')}: 시스템 초기화 완료
"""
        
        with open(self.ai_dir / "ledgers" / "_active.md", "w", encoding="utf-8") as f:
            f.write(active_md)
    
    def _create_ai_tool_configs(self, project_name: str) -> None:
        """AI 도구 설정 파일 생성"""
        self._log_info("AI 도구 설정 파일을 생성합니다...")
        
        # Cursor 설정
        cursor_rules = f"""# {project_name} - Cursor AI 규칙

## 프로젝트 맥락
이 프로젝트는 GridFile-Wrinkl 하이브리드 시스템을 사용합니다.

## 필수 확인사항
1. .ai/ledgers/에서 현재 작업 중인 기능 확인
2. .ai/patterns.md의 코딩 패턴 준수
3. .ai/context-rules.md의 가이드라인 준수

## 파일 작업 시
- 새 파일 생성 시 GridFile 블록 할당 고려
- 기능별로 일관된 디렉토리 구조 유지
- 변경사항을 해당 기능의 ledger에 기록

## 코드 스타일
- 주석: 한국어
- 함수명: snake_case
- 클래스명: PascalCase
- 타입 힌트 필수

## 금지사항
- 전역 변수 남용
- 매직 넘버 사용
- 과도한 중첩 (3단계 이상)
- 테스트 없는 코드 작성
"""
        
        with open(self.project_path / ".cursorrules", "w", encoding="utf-8") as f:
            f.write(cursor_rules)
        
        # GitHub Copilot 설정
        github_dir = self.project_path / ".github"
        github_dir.mkdir(exist_ok=True)
        
        copilot_instructions = f"""# {project_name} - GitHub Copilot 지침

이 프로젝트는 GridFile-Wrinkl 통합 시스템을 사용합니다.

## 작업 전 체크리스트
- [ ] .ai/ledgers/에서 현재 기능 컨텍스트 확인
- [ ] .ai/patterns.md의 코딩 패턴 검토
- [ ] .ai/architecture.md의 설계 원칙 확인

## 코드 생성 가이드라인
- 한국어 주석 사용
- 타입 힌트 포함
- 에러 처리 구현
- 테스트 코드 생성

## 파일 관리
- 새 파일은 적절한 GridFile 존에 배치
- 기능별 디렉토리 구조 유지
- 임시 파일은 .tmp/ 사용

## 문서화
- 함수 docstring 필수
- 복잡한 로직은 인라인 주석
- 변경사항을 ledger에 기록
"""
        
        with open(github_dir / "copilot-instructions.md", "w", encoding="utf-8") as f:
            f.write(copilot_instructions)
    
    def _scan_and_organize_files(self) -> None:
        """기존 프로젝트 파일 스캔 및 분석"""
        self._log_info("프로젝트 파일을 스캔하고 분석합니다...")
        
        # 파일 수집
        files = []
        for file_path in self.project_path.glob("**/*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                files.append(file_path)
        
        self._log_info(f"{len(files)}개의 파일을 발견했습니다.")
        
        # 파일 분류 및 초기 그리드 레이아웃 생성
        grid_layout = self._create_initial_grid_layout(files)
        
        # 레이아웃 저장
        layout_path = self.gridfile_dir / "layouts" / "initial.json"
        with open(layout_path, "w", encoding="utf-8") as f:
            json.dump(grid_layout, f, indent=2, ensure_ascii=False)
            
        self._log_debug(f"초기 그리드 레이아웃 저장: {layout_path}")
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """무시해야 할 파일인지 확인"""
        ignore_patterns = [
            ".git", "__pycache__", ".venv", "node_modules",
            ".ai", ".gridfile", ".tmp", "dist", "build"
        ]
        
        str_path = str(file_path)
        return any(pattern in str_path for pattern in ignore_patterns)
    
    def _create_initial_grid_layout(self, files: List[Path]) -> Dict:
        """초기 그리드 레이아웃 생성"""
        # 파일 분석
        file_blocks = []
        for file_path in files:
            file_info = self._analyze_file(file_path)
            file_blocks.append({
                "path": str(file_path.relative_to(self.project_path)),
                "name": file_path.name,
                "type": file_info["type"],
                "category": file_info["category"],
                "size": file_info["size"],
                "modified": file_info["modified"],
                "placed": False
            })
        
        # 레이아웃 생성
        layout = {
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "grid_size": self.config["grid_size"],
            "zones": self.config["zones"],
            "blocks": file_blocks,
            "stats": {
                "total_files": len(file_blocks),
                "placed_files": 0,
                "by_category": {},
                "by_type": {}
            }
        }
        
        # 통계 집계
        category_counts = {}
        type_counts = {}
        
        for block in file_blocks:
            category = block["category"]
            file_type = block["type"]
            
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
                
            if file_type in type_counts:
                type_counts[file_type] += 1
            else:
                type_counts[file_type] = 1
        
        layout["stats"]["by_category"] = category_counts
        layout["stats"]["by_type"] = type_counts
        
        return layout
    
    def _analyze_file(self, file_path: Path) -> Dict:
        """파일 분석"""
        stats = file_path.stat()
        
        # 파일 타입 추론
        ext = file_path.suffix.lower()
        file_type = "unknown"
        
        if ext in [".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs"]:
            file_type = "code"
        elif ext in [".md", ".txt", ".doc", ".docx", ".pdf"]:
            file_type = "document"
        elif ext in [".json", ".yaml", ".yml", ".toml", ".ini", ".config"]:
            file_type = "config"
        elif ext in [".jpg", ".png", ".gif", ".svg", ".webp"]:
            file_type = "image"
        elif ext in [".html", ".css", ".scss", ".sass"]:
            file_type = "web"
        elif ext in [".sql", ".db"]:
            file_type = "database"
        elif ext in [".zip", ".tar", ".gz", ".rar"]:
            file_type = "archive"
        
        # 카테고리 추론 (수정 시간 기준)
        days_since_modified = (datetime.datetime.now() - 
                              datetime.datetime.fromtimestamp(stats.st_mtime)).days
        
        if days_since_modified < 7:
            category = "active"
        elif days_since_modified < 30:
            category = "pending"
        else:
            category = "archive"
            
        # 특수 파일 처리
        if file_path.name.startswith("README"):
            category = "resources"
        elif file_path.name in ["requirements.txt", "package.json", "setup.py"]:
            category = "resources"
        elif file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
            category = "resources"
        
        return {
            "type": file_type,
            "category": category,
            "size": stats.st_size,
            "modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat()
        }

    def create_feature(self, feature_name: str, description: str = "", skip_dash_conversion: bool = False) -> str:
        """
        새로운 기능 개발을 시작하기 위한 원장(ledger) 파일 생성
        
        Args:
            feature_name: 기능 이름
            description: 기능 설명
            skip_dash_conversion: 기능명의 밑줄을 대시로 변환하지 않음
            
        Returns:
            str: 생성된 원장 파일 경로
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return ""
        
        # 기능명 정규화
        if not skip_dash_conversion:
            feature_name = feature_name.replace("-", "_")
        
        ledger_path = self.ai_dir / "ledgers" / "active" / f"{feature_name}.md"
        if ledger_path.exists():
            self._log_warning(f"'{feature_name}' 기능의 원장 파일이 이미 존재합니다.")
            return str(ledger_path)
        
        self._log_info(f"'{feature_name}' 기능의 개발을 시작합니다...")
        
        ledger_content = f"""# {feature_name} - 기능 개발 원장

## 기본 정보
- **기능명**: {feature_name}
- **생성일**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **상태**: 개발 중
- **담당자**: TBD

## 요구사항
{description or '- TBD'}

## 기술적 접근
- **사용 기술**: TBD
- **아키텍처**: TBD
- **의존성**: TBD

## 개발 진행사항
### {datetime.datetime.now().strftime('%Y-%m-%d')}
- 기능 원장 생성
- 초기 기획 시작

## 파일 구조
```
관련 파일들이 여기에 표시됩니다
```

## GridFile 블록 정보
- **배치 존**: active (활성 개발)
- **블록 크기**: 표준 (2x2)
- **색상**: 빨간색 (활성 프로젝트)

## 테스트 계획
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] 사용자 테스트 계획

## 완료 체크리스트
- [ ] 코드 구현 완료
- [ ] 테스트 통과
- [ ] 문서 업데이트
- [ ] 코드 리뷰 완료
- [ ] 배포 완료

## 회고
*완료 후 작성*
"""
        
        # 원장 파일 생성
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write(ledger_content)
        
        self._update_active_dashboard()
        self._log_success(f"'{feature_name}' 기능 원장이 생성되었습니다: {ledger_path}")
        
        return str(ledger_path)
    
    def _update_active_dashboard(self) -> None:
        """활성 기능 대시보드 업데이트"""
        active_ledgers = list((self.ai_dir / "ledgers" / "active").glob("*.md"))
        active_features = []
        
        for ledger in active_ledgers:
            if ledger.name != "_active.md":
                active_features.append(ledger.stem)
        
        dashboard_content = f"""# 활성 기능 대시보드

## 현재 개발 중인 기능
*마지막 업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

"""
        
        if active_features:
            dashboard_content += "## 활성 기능 목록\n"
            for feature in active_features:
                dashboard_content += f"- **{feature}**: `.ai/ledgers/active/{feature}.md`\n"
        else:
            dashboard_content += """## 활성 기능 목록
- 아직 등록된 기능이 없습니다
- `gridwrinkl feature <feature-name>` 명령어로 새 기능을 시작하세요
"""
        
        dashboard_content += f"""
## GridFile 상태
- **활성 기능**: {len(active_features)}개
- **그리드 효율성**: {min(100, len(active_features) * 10)}%

## 최근 활동
- {datetime.datetime.now().strftime('%Y-%m-%d')}: 대시보드 업데이트
"""
        
        dashboard_path = self.ai_dir / "ledgers" / "_active.md"
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(dashboard_content)
        
        self._log_debug("활성 기능 대시보드 업데이트 완료")
    
    def list_features(self, include_archived: bool = False) -> List[Dict]:
        """
        기능 목록 조회
        
        Args:
            include_archived: 아카이브된 기능도 포함할지 여부
            
        Returns:
            List[Dict]: 기능 목록 (이름, 상태, 경로 포함)
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return []
        
        features = []
        
        # 활성 기능 조회
        for ledger_path in (self.ai_dir / "ledgers" / "active").glob("*.md"):
            if ledger_path.name == "_active.md":
                continue
                
            features.append({
                "name": ledger_path.stem,
                "status": "active",
                "path": str(ledger_path.relative_to(self.project_path))
            })
        
        # 아카이브된 기능 조회
        if include_archived:
            for ledger_path in (self.ai_dir / "ledgers" / "archived").glob("*.md"):
                features.append({
                    "name": ledger_path.stem,
                    "status": "archived",
                    "path": str(ledger_path.relative_to(self.project_path))
                })
        
        return features
    
    def archive_feature(self, feature_name: str) -> bool:
        """
        기능 아카이브 처리
        
        Args:
            feature_name: 아카이브할 기능 이름
            
        Returns:
            bool: 아카이브 성공 여부
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return False
        
        # 기능명 정규화
        feature_name = feature_name.replace("-", "_")
        
        active_path = self.ai_dir / "ledgers" / "active" / f"{feature_name}.md"
        archived_path = self.ai_dir / "ledgers" / "archived" / f"{feature_name}.md"
        
        if not active_path.exists():
            self._log_error(f"'{feature_name}' 기능을 찾을 수 없습니다.")
            return False
        
        self._log_info(f"'{feature_name}' 기능을 아카이브합니다...")
        
        # 원장 파일 내용 읽기
        with open(active_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 아카이브 정보 추가
        archive_info = f"""

## 아카이브 정보
- **아카이브 일시**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **최종 상태**: 완료
- **GridFile 상태**: archive 영역으로 이동됨
"""
        
        # 아카이브 파일 생성
        with open(archived_path, "w", encoding="utf-8") as f:
            f.write(content + archive_info)
        
        # 활성 파일 삭제
        active_path.unlink()
        
        self._update_active_dashboard()
        self._log_success(f"'{feature_name}' 기능이 아카이브되었습니다.")
        
        return True

    def context_snapshot(self, name: str = "") -> str:
        """
        현재 맥락의 스냅샷 생성
        
        Args:
            name: 스냅샷 이름 (기본값: 타임스탬프)
            
        Returns:
            str: 스냅샷 디렉토리 경로
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return ""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_name = name if name else f"snapshot-{timestamp}"
        
        self._log_info(f"'{snapshot_name}' 맥락 스냅샷을 생성합니다...")
        
        # 스냅샷 디렉토리 생성
        snapshot_dir = self.ai_dir / "context-snapshots" / snapshot_name
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # AI 디렉토리 내용 복사
        ai_files = [
            "project.md",
            "patterns.md",
            "architecture.md",
            "context-rules.md"
        ]
        
        for file_name in ai_files:
            src_path = self.ai_dir / file_name
            if src_path.exists():
                shutil.copy2(src_path, snapshot_dir)
        
        # 활성 기능 원장 복사
        ledgers_dir = snapshot_dir / "ledgers"
        ledgers_dir.mkdir(exist_ok=True)
        
        for ledger_path in (self.ai_dir / "ledgers" / "active").glob("*.md"):
            shutil.copy2(ledger_path, ledgers_dir)
        
        # 그리드 레이아웃 복사
        if (self.gridfile_dir / "layouts" / "current.json").exists():
            shutil.copy2(
                self.gridfile_dir / "layouts" / "current.json", 
                snapshot_dir / "grid-layout.json"
            )
        
        self._log_success(f"맥락 스냅샷 '{snapshot_name}'이(가) 생성되었습니다.")
        return str(snapshot_dir)
    
    def sync_ai_tools(self) -> bool:
        """
        AI 도구 설정 파일을 현재 맥락과 동기화
        
        Returns:
            bool: 동기화 성공 여부
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return False
        
        self._log_info("AI 도구 설정 파일을 현재 맥락과 동기화합니다...")
        
        # 프로젝트 설정 로드
        if not self.config:
            config_path = self.gridfile_dir / "config.json"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self._log_error("설정 파일을 찾을 수 없습니다.")
                return False
        
        project_name = self.config.get("project_name", "Project")
        ai_tools = self.config.get("ai_tools", ["cursor", "copilot"])
        
        # 지원되는 도구만 필터링
        supported_tools = [tool for tool in ai_tools if tool in self.ai_tools]
        
        if not supported_tools:
            self._log_warning("지원되는 AI 도구가 설정되지 않았습니다.")
            return False
        
        # 활성 기능 목록 조회
        features = self.list_features()
        feature_names = [feature["name"] for feature in features]
        
        # 도구별 설정 파일 업데이트
        updated_tools = []
        
        for tool in supported_tools:
            if tool == "cursor":
                self._update_cursor_rules(project_name, feature_names)
                updated_tools.append("cursor")
            elif tool == "copilot":
                self._update_copilot_instructions(project_name, feature_names)
                updated_tools.append("copilot")
        
        if updated_tools:
            self._log_success(f"다음 AI 도구 설정이 업데이트되었습니다: {', '.join(updated_tools)}")
            return True
        else:
            self._log_warning("업데이트된 AI 도구 설정이 없습니다.")
            return False
    
    def _update_cursor_rules(self, project_name: str, features: List[str]) -> None:
        """Cursor AI 규칙 업데이트"""
        cursor_rules = f"""# {project_name} - Cursor AI 규칙
# [자동 생성됨: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}]

## 프로젝트 맥락
이 프로젝트는 GridFile-Wrinkl 하이브리드 시스템을 사용합니다.

## 현재 작업 중인 기능
{', '.join(features) if features else "현재 작업 중인 기능이 없습니다."}

## 필수 확인사항
1. .ai/ledgers/에서 현재 작업 중인 기능 확인
2. .ai/patterns.md의 코딩 패턴 준수
3. .ai/context-rules.md의 가이드라인 준수

## 파일 작업 시
- 새 파일 생성 시 GridFile 블록 할당 고려
- 기능별로 일관된 디렉토리 구조 유지
- 변경사항을 해당 기능의 ledger에 기록

## 코드 스타일
- 주석: 한국어
- 함수명: snake_case
- 클래스명: PascalCase
- 타입 힌트 필수

## 금지사항
- 전역 변수 남용
- 매직 넘버 사용
- 과도한 중첩 (3단계 이상)
- 테스트 없는 코드 작성
"""
        
        with open(self.project_path / ".cursorrules", "w", encoding="utf-8") as f:
            f.write(cursor_rules)
    
    def _update_copilot_instructions(self, project_name: str, features: List[str]) -> None:
        """GitHub Copilot 지침 업데이트"""
        github_dir = self.project_path / ".github"
        github_dir.mkdir(exist_ok=True)
        
        copilot_instructions = f"""# {project_name} - GitHub Copilot 지침
# [자동 생성됨: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}]

이 프로젝트는 GridFile-Wrinkl 통합 시스템을 사용합니다.

## 현재 작업 중인 기능
{', '.join(features) if features else "현재 작업 중인 기능이 없습니다."}

## 작업 전 체크리스트
- [ ] .ai/ledgers/에서 현재 기능 컨텍스트 확인
- [ ] .ai/patterns.md의 코딩 패턴 검토
- [ ] .ai/architecture.md의 설계 원칙 확인

## 코드 생성 가이드라인
- 한국어 주석 사용
- 타입 힌트 포함
- 에러 처리 구현
- 테스트 코드 생성

## 파일 관리
- 새 파일은 적절한 GridFile 존에 배치
- 기능별 디렉토리 구조 유지
- 임시 파일은 .tmp/ 사용

## 문서화
- 함수 docstring 필수
- 복잡한 로직은 인라인 주석
- 변경사항을 ledger에 기록
"""
        
        with open(github_dir / "copilot-instructions.md", "w", encoding="utf-8") as f:
            f.write(copilot_instructions)

    def grid_reorganize(self) -> bool:
        """
        그리드 레이아웃 재구성 및 최적화
        
        Returns:
            bool: 재구성 성공 여부
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return False
        
        self._log_info("그리드 레이아웃을 재구성합니다...")
        
        # 현재 레이아웃 로드
        current_layout_path = self.gridfile_dir / "layouts" / "current.json"
        initial_layout_path = self.gridfile_dir / "layouts" / "initial.json"
        
        layout_path = current_layout_path if current_layout_path.exists() else initial_layout_path
        
        if not layout_path.exists():
            self._log_error("그리드 레이아웃 파일을 찾을 수 없습니다.")
            return False
        
        with open(layout_path, "r", encoding="utf-8") as f:
            layout = json.load(f)
        
        # 그리드 크기 확인
        grid_size = layout.get("grid_size", {"width": 12, "height": 8})
        zones = layout.get("zones", {
            "active": {"x": 0, "y": 0, "width": 6, "height": 4},
            "resources": {"x": 6, "y": 0, "width": 6, "height": 4},
            "archive": {"x": 0, "y": 4, "width": 12, "height": 4}
        })
        
        # 블록 목록과 상태 확인
        blocks = layout.get("blocks", [])
        old_placed = sum(1 for block in blocks if block.get("placed", False))
        
        # 블록 재배치
        self._log_info("블록을 재배치하여 그리드 효율성을 개선합니다...")
        new_blocks = self._reorganize_blocks(blocks, zones, grid_size)
        
        # 새 레이아웃 저장
        new_layout = {
            "version": "1.0.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "grid_size": grid_size,
            "zones": zones,
            "blocks": new_blocks,
            "stats": {
                "total_files": len(new_blocks),
                "placed_files": sum(1 for block in new_blocks if block.get("placed", False)),
                "by_category": {},
                "by_type": {}
            }
        }
        
        # 통계 업데이트
        category_counts = {}
        type_counts = {}
        
        for block in new_blocks:
            category = block["category"]
            file_type = block["type"]
            
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
                
            if file_type in type_counts:
                type_counts[file_type] += 1
            else:
                type_counts[file_type] = 1
        
        new_layout["stats"]["by_category"] = category_counts
        new_layout["stats"]["by_type"] = type_counts
        
        # 이전 레이아웃 백업
        if layout_path.exists():
            backup_path = self.gridfile_dir / "backups" / f"layout-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            shutil.copy2(layout_path, backup_path)
        
        # 새 레이아웃 저장
        with open(self.gridfile_dir / "layouts" / "current.json", "w", encoding="utf-8") as f:
            json.dump(new_layout, f, indent=2, ensure_ascii=False)
        
        # 개선 사항 로깅
        new_placed = sum(1 for block in new_blocks if block.get("placed", False))
        if len(blocks) > 0:
            old_efficiency = old_placed / len(blocks) * 100
            new_efficiency = new_placed / len(blocks) * 100
            self._log_success(f"그리드 효율성이 {old_efficiency:.1f}%에서 {new_efficiency:.1f}%로 개선되었습니다.")
        else:
            self._log_success("그리드 레이아웃이 재구성되었습니다.")
        
        return True
    
    def _reorganize_blocks(self, blocks: List[Dict], zones: Dict, grid_size: Dict) -> List[Dict]:
        """블록 재배치 최적화"""
        # 그리드 점유 상태 초기화
        grid = [[False for _ in range(grid_size["width"])] for _ in range(grid_size["height"])]
        
        # 블록 카테고리별 분류
        categorized_blocks = {}
        for block in blocks:
            category = block["category"]
            if category not in categorized_blocks:
                categorized_blocks[category] = []
            categorized_blocks[category].append(block.copy())
        
        # 모든 블록을 미배치 상태로 초기화
        for blocks_list in categorized_blocks.values():
            for block in blocks_list:
                block["placed"] = False
                if "position" in block:
                    del block["position"]
        
        # 영역별로 블록 배치
        for category, blocks_list in categorized_blocks.items():
            zone_name = self.category_to_zone.get(category, "archive")
            if zone_name in zones:
                zone = zones[zone_name]
                self._place_blocks_in_zone(blocks_list, zone, grid)
        
        # 모든 블록 병합하여 반환
        result_blocks = []
        for blocks_list in categorized_blocks.values():
            result_blocks.extend(blocks_list)
        
        return result_blocks
    
    def _place_blocks_in_zone(self, blocks: List[Dict], zone: Dict, grid: List[List[bool]]) -> None:
        """특정 영역에 블록 배치"""
        zone_x, zone_y = zone["x"], zone["y"]
        zone_w, zone_h = zone["width"], zone["height"]
        
        # 영역 내 좌표 순회
        for y in range(zone_y, zone_y + zone_h):
            for x in range(zone_x, zone_x + zone_w):
                if y >= len(grid) or x >= len(grid[0]):
                    continue
                    
                # 이미 점유된 셀이면 건너뛰기
                if grid[y][x]:
                    continue
                
                # 배치할 블록이 없으면 종료
                if not blocks:
                    return
                
                # 다음 블록 배치
                block = blocks.pop(0)
                block["placed"] = True
                block["position"] = {"x": x, "y": y}
                grid[y][x] = True
    
    def ui(self, port: int = 3000) -> None:
        """
        그래픽 UI 시작
        
        Args:
            port: 웹 서버 포트
        """
        if not self.is_initialized():
            self._log_error("GridWrinkl이 초기화되지 않았습니다. 먼저 'gridwrinkl init' 명령을 실행하세요.")
            return
        
        self._log_info(f"GridWrinkl UI를 포트 {port}에서 시작합니다...")
        self._log_warning("이 기능은 현재 개발 중입니다.")
        self._log_info(f"http://localhost:{port}에서 웹 인터페이스에 접속하세요.")
        
        # 실제 구현에서는 여기서 웹 서버 시작
        print("\n실제 웹 UI 구현은 현재 준비 중입니다.\n")


def create_parser() -> argparse.ArgumentParser:
    """명령줄 인터페이스 파서 생성"""
    parser = argparse.ArgumentParser(
        prog="gridwrinkl",
        description="GridWrinkl CLI - GridFile과 Wrinkl 시스템을 통합한 개발 생산성 도구",
        epilog="자세한 내용은 매뉴얼을 참조하세요."
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--path", "-p",
        help="프로젝트 경로 (기본값: 현재 디렉토리)",
        default="."
    )
    
    parser.add_argument(
        "--debug",
        help="디버그 모드 활성화",
        action="store_true"
    )
    
    parser.add_argument(
        "--no-color",
        help="색상 출력 비활성화",
        action="store_true"
    )
    
    # 서브커맨드 추가
    subparsers = parser.add_subparsers(dest="command", help="수행할 명령")
    
    # init 명령
    init_parser = subparsers.add_parser("init", help="프로젝트 초기화")
    init_parser.add_argument("project_name", help="프로젝트 이름")
    init_parser.add_argument(
        "--force", "-f",
        help="기존 설정 강제 덮어쓰기",
        action="store_true"
    )
    
    # feature 명령 그룹
    feature_parser = subparsers.add_parser("feature", help="기능 관리")
    feature_subparsers = feature_parser.add_subparsers(dest="feature_command", help="기능 관련 명령")
    
    # feature create
    feature_create_parser = feature_subparsers.add_parser("create", help="새 기능 생성")
    feature_create_parser.add_argument("feature_name", help="기능 이름")
    feature_create_parser.add_argument(
        "--description", "-d",
        help="기능 설명",
        default=""
    )
    feature_create_parser.add_argument(
        "--no-dash-conversion",
        help="기능명의 대시(-)를 밑줄(_)로 변환하지 않음",
        action="store_true"
    )
    
    # feature list
    feature_list_parser = feature_subparsers.add_parser("list", help="기능 목록 조회")
    feature_list_parser.add_argument(
        "--all", "-a",
        help="아카이브된 기능도 포함",
        action="store_true"
    )
    feature_list_parser.add_argument(
        "--json",
        help="JSON 형식으로 출력",
        action="store_true"
    )
    
    # feature archive
    feature_archive_parser = feature_subparsers.add_parser("archive", help="기능 아카이브")
    feature_archive_parser.add_argument("feature_name", help="아카이브할 기능 이름")
    
    # context 명령 그룹
    context_parser = subparsers.add_parser("context", help="맥락 관리")
    context_subparsers = context_parser.add_subparsers(dest="context_command", help="맥락 관련 명령")
    
    # context snapshot
    context_snapshot_parser = context_subparsers.add_parser("snapshot", help="맥락 스냅샷 생성")
    context_snapshot_parser.add_argument(
        "--name", "-n",
        help="스냅샷 이름 (기본값: 타임스탬프)",
        default=""
    )
    
    # context sync
    context_sync_parser = context_subparsers.add_parser("sync", help="AI 도구와 맥락 동기화")
    
    # grid 명령 그룹
    grid_parser = subparsers.add_parser("grid", help="그리드 관리")
    grid_subparsers = grid_parser.add_subparsers(dest="grid_command", help="그리드 관련 명령")
    
    # grid reorganize
    grid_reorganize_parser = grid_subparsers.add_parser("reorganize", help="그리드 재구성")
    
    # ui 명령
    ui_parser = subparsers.add_parser("ui", help="그래픽 UI 시작")
    ui_parser.add_argument(
        "--port", "-p",
        help="웹 서버 포트 (기본값: 3000)",
        type=int,
        default=3000
    )
    
    return parser


def handle_feature_command(gridwrinkl: GridWrinkl, args: argparse.Namespace) -> None:
    """feature 명령 처리"""
    if args.feature_command == "create":
        gridwrinkl.create_feature(
            args.feature_name,
            args.description,
            args.no_dash_conversion
        )
    
    elif args.feature_command == "list":
        features = gridwrinkl.list_features(args.all)
        
        if args.json:
            print(json.dumps(features, indent=2))
        else:
            print("\n현재 기능 목록:")
            
            if not features:
                print("  기능이 없습니다.")
            else:
                for feature in features:
                    status_color = ConsoleColors.GREEN if feature["status"] == "active" else ConsoleColors.YELLOW
                    status_text = "활성" if feature["status"] == "active" else "아카이브됨"
                    
                    if not args.no_color:
                        print(f"  • {feature['name']} ({status_color}{status_text}{ConsoleColors.ENDC})")
                        print(f"    경로: {feature['path']}")
                    else:
                        print(f"  • {feature['name']} ({status_text})")
                        print(f"    경로: {feature['path']}")
    
    elif args.feature_command == "archive":
        gridwrinkl.archive_feature(args.feature_name)
    
    else:
        # 기본 동작: feature create와 동일하게 처리
        gridwrinkl.create_feature(args.feature_name)


def handle_context_command(gridwrinkl: GridWrinkl, args: argparse.Namespace) -> None:
    """context 명령 처리"""
    if args.context_command == "snapshot":
        gridwrinkl.context_snapshot(args.name)
    
    elif args.context_command == "sync":
        gridwrinkl.sync_ai_tools()
    
    else:
        gridwrinkl._log_error("알 수 없는 context 하위 명령입니다.")


def handle_grid_command(gridwrinkl: GridWrinkl, args: argparse.Namespace) -> None:
    """grid 명령 처리"""
    if args.grid_command == "reorganize":
        gridwrinkl.grid_reorganize()
    
    else:
        gridwrinkl._log_error("알 수 없는 grid 하위 명령입니다.")


def main() -> None:
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 경로 및 옵션 설정
    path = args.path
    debug = args.debug
    no_color = args.no_color
    
    # GridWrinkl 인스턴스 생성
    gridwrinkl = GridWrinkl(path, debug)
    
    # 색상 설정
    if no_color:
        gridwrinkl.color_enabled = False
    
    # 명령 분기 처리
    if args.command == "init":
        gridwrinkl.init(args.project_name, args.force)
    
    elif args.command == "feature":
        handle_feature_command(gridwrinkl, args)
    
    elif args.command == "context":
        handle_context_command(gridwrinkl, args)
    
    elif args.command == "grid":
        handle_grid_command(gridwrinkl, args)
    
    elif args.command == "ui":
        gridwrinkl.ui(args.port)
    
    else:
        # 명령이 제공되지 않은 경우 도움말 출력
        parser.print_help()


if __name__ == "__main__":
    main()
