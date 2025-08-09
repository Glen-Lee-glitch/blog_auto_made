# Blog Writing Generator

Git 커밋 로그와 코드 변경점을 분석하여 기술 블로그 포스트를 자동으로 생성하는 도구입니다.

## 🚀 주요 기능

- Git 커밋 로그 분석
- 코드 변경점 추출
- LLM을 활용한 블로그 내용 생성
- Markdown 형식의 블로그 포스트 자동 생성

## 📋 요구사항

- Python 3.10+
- Git 리포지토리 접근 권한
- OpenAI API 키 (또는 다른 LLM 서비스)

## 🛠️ 설치 방법

1. 리포지토리 클론
```bash
git clone <your-repository-url>
cd blog_writing
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경변수 설정
```bash
cp .env.example .env
# .env 파일에 API 키 등 필요한 정보 입력
```

## 📁 프로젝트 구조

```
blog_writing/
├── src/
│   ├── git_analyzer.py      # Git 로그 분석
│   ├── content_generator.py # LLM 내용 생성
│   ├── post_formatter.py    # Markdown 포맷팅
│   └── main.py             # 메인 실행 파일
├── tests/                  # 테스트 파일
├── docs/                   # 문서
├── requirements.txt        # Python 의존성
└── README.md              # 프로젝트 설명
```

## 🎯 사용 방법

```bash
python src/main.py
```

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
