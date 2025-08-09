# Git 커밋 로그 기반 자동 블로그 생성기 개발기

## ✨ 들어가며

오늘은 Git 커밋 로그를 분석하여 기술 블로그 포스트를 자동으로 생성하는 시스템을 개발했습니다. 이 프로젝트는 개발자들이 매일 작성하는 Git 커밋을 바탕으로 의미 있는 기술 블로그를 자동으로 생성하여, 개발 과정을 기록하고 지식을 공유하는 데 도움을 주는 것이 목표입니다.

## 📝 주요 변경 사항

### (7a3e5cd) GitPython 호환성 문제 및 OpenAI API 1.0+ 버전 대응

이번 커밋에서는 실제 테스트 과정에서 발견된 여러 기술적 문제들을 해결했습니다:

```python
# GitPython Diff 객체 stats 속성 접근 오류 수정
try:
    additions = diff.stats.get('insertions', 0)
    deletions = diff.stats.get('deletions', 0)
except AttributeError:
    additions = 0
    deletions = 0
```

```python
# OpenAI API 1.0+ 버전에 맞는 클라이언트 호출 방식
client = openai.OpenAI(api_key=self.api_key)
response = client.chat.completions.create(
    model=self.model,
    messages=[...],
    max_tokens=100,
    temperature=0.7
)
```

### (244bd13d) 블로그 자동 생성 시스템 핵심 모듈 구현

이 커밋에서는 전체 시스템의 핵심 모듈들을 구현했습니다:

#### 1. GitAnalyzer 모듈
- Git 커밋 로그 분석 및 변경사항 추출
- 파일별 변경 타입 (추가/수정/삭제) 식별
- 리포지토리 통계 정보 수집

#### 2. ContentGenerator 모듈
- OpenAI API를 활용한 블로그 내용 생성
- 커밋 메시지 기반 제목 자동 생성
- Rule에 정의된 형식의 본문 생성

#### 3. PostFormatter 모듈
- Markdown 형식 포맷팅 및 메타데이터 생성
- 파일 저장 및 관리 기능
- 요약 파일 자동 생성

#### 4. 메인 시스템
- 전체 프로세스 조율 및 명령행 인터페이스
- 로깅 및 오류 처리

### (6a6f414) 프로젝트 기본 구조 설정

프로젝트의 초기 설정을 완료했습니다:

```
blog_writing/
├── src/
│   ├── git_analyzer.py      # Git 분석
│   ├── content_generator.py # LLM 내용 생성
│   ├── post_formatter.py    # Markdown 포맷팅
│   └── main.py             # 메인 실행 파일
├── tests/                  # 테스트 파일
├── docs/                   # 문서
├── requirements.txt        # Python 의존성
└── README.md              # 프로젝트 설명
```

## 💡 구현 과정 및 배운 점

### 1. GitPython 라이브러리 활용

GitPython을 사용하여 Git 리포지토리를 분석하는 과정에서 몇 가지 중요한 점을 배웠습니다:

- **커밋 객체 접근**: `repo.iter_commits()`를 통해 커밋 히스토리에 접근
- **Diff 분석**: `commit.diff(parent)`를 통해 변경사항 추출
- **통계 정보**: `commit.stats`를 통해 추가/삭제된 라인 수 확인

### 2. OpenAI API 1.0+ 버전 대응

OpenAI API의 최신 버전에서는 클라이언트 생성 방식이 변경되었습니다:

```python
# 이전 방식 (0.x 버전)
response = openai.ChatCompletion.create(...)

# 새로운 방식 (1.0+ 버전)
client = openai.OpenAI(api_key=api_key)
response = client.chat.completions.create(...)
```

### 3. 모듈화와 설계 패턴

이 프로젝트에서는 다음과 같은 설계 원칙을 적용했습니다:

- **단일 책임 원칙**: 각 모듈이 하나의 명확한 역할을 담당
- **의존성 주입**: 외부 라이브러리와의 결합도 최소화
- **에러 처리**: 각 단계에서 적절한 예외 처리 및 로깅

### 4. 테스트 주도 개발

실제 테스트를 통해 여러 문제점을 발견하고 해결할 수 있었습니다:

- GitPython의 Diff 객체에서 stats 속성 접근 오류
- OpenAI API 버전 호환성 문제
- import 경로 문제

## ✅ 마무리

이번 프로젝트를 통해 Git 커밋 로그를 활용한 자동화된 블로그 생성 시스템의 기본 틀을 완성했습니다. 앞으로 다음과 같은 개선사항을 고려해볼 예정입니다:

1. **다양한 LLM 지원**: OpenAI 외에 다른 AI 모델 지원
2. **템플릿 시스템**: 다양한 블로그 스타일 지원
3. **웹 인터페이스**: 사용자 친화적인 웹 UI 개발
4. **스케줄링**: 정기적인 블로그 포스트 자동 생성

이 시스템이 개발자들의 기술 블로그 작성에 도움이 되길 바랍니다! 🚀

---

*이 포스트는 실제 Git 커밋 로그를 분석하여 작성되었습니다.*
