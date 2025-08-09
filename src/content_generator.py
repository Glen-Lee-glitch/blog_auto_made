"""
LLM을 사용하여 Git 커밋 정보를 바탕으로 블로그 내용을 생성하는 모듈

이 모듈은 OpenAI API를 사용하여 Git 커밋 로그를 분석하고,
기술 블로그 포스트의 내용을 자동으로 생성합니다.
"""

import logging
import os
from typing import List, Dict, Optional
from datetime import datetime
import openai
from dotenv import load_dotenv
from .git_analyzer import CommitInfo, FileChange

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentGenerator:
    """LLM을 사용하여 블로그 내용을 생성하는 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        ContentGenerator 초기화
        
        Args:
            api_key: OpenAI API 키 (None인 경우 환경변수에서 로드)
            model: 사용할 OpenAI 모델명
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        
        if not self.api_key:
            raise ValueError("OpenAI API 키가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 직접 전달하세요.")
        
        openai.api_key = self.api_key
        logger.info(f"ContentGenerator 초기화 완료 (모델: {self.model})")
    
    def generate_blog_content(self, commits: List[CommitInfo], file_changes: List[FileChange] = None) -> Dict[str, str]:
        """
        Git 커밋 정보를 바탕으로 블로그 내용을 생성합니다
        
        Args:
            commits: 커밋 정보 리스트
            file_changes: 파일 변경 정보 리스트 (선택사항)
            
        Returns:
            생성된 블로그 내용 (제목, 본문 등)
        """
        try:
            # 커밋 정보를 텍스트로 변환
            commit_summary = self._format_commits_for_llm(commits)
            
            # 파일 변경 정보가 있으면 추가
            if file_changes:
                file_summary = self._format_file_changes_for_llm(file_changes)
                commit_summary += f"\n\n파일 변경 상세:\n{file_summary}"
            
            # 블로그 제목 생성
            title = self._generate_title(commits)
            
            # 블로그 본문 생성
            content = self._generate_content(commit_summary)
            
            return {
                'title': title,
                'content': content,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"블로그 내용 생성 중 오류 발생: {e}")
            return {
                'title': '오늘의 개발 일지',
                'content': '내용 생성 중 오류가 발생했습니다.',
                'error': str(e)
            }
    
    def _format_commits_for_llm(self, commits: List[CommitInfo]) -> str:
        """
        커밋 정보를 LLM이 이해하기 쉬운 형태로 포맷팅합니다
        
        Args:
            commits: 커밋 정보 리스트
            
        Returns:
            포맷팅된 커밋 정보 텍스트
        """
        if not commits:
            return "최근 커밋이 없습니다."
        
        formatted_commits = []
        for commit in commits:
            formatted_commit = f"""
커밋: {commit.hash}
작성자: {commit.author}
날짜: {commit.date.strftime('%Y-%m-%d %H:%M:%S')}
메시지: {commit.message}
변경된 파일: {', '.join(commit.files_changed)}
추가된 라인: {commit.additions}, 삭제된 라인: {commit.deletions}
"""
            formatted_commits.append(formatted_commit)
        
        return "\n".join(formatted_commits)
    
    def _format_file_changes_for_llm(self, file_changes: List[FileChange]) -> str:
        """
        파일 변경 정보를 LLM이 이해하기 쉬운 형태로 포맷팅합니다
        
        Args:
            file_changes: 파일 변경 정보 리스트
            
        Returns:
            포맷팅된 파일 변경 정보 텍스트
        """
        if not file_changes:
            return ""
        
        formatted_changes = []
        for change in file_changes:
            change_type_text = {
                'A': '추가',
                'M': '수정',
                'D': '삭제'
            }.get(change.change_type, change.change_type)
            
            formatted_change = f"""
파일: {change.file_path}
변경 타입: {change_type_text}
추가된 라인: {change.additions}, 삭제된 라인: {change.deletions}
"""
            formatted_changes.append(formatted_change)
        
        return "\n".join(formatted_changes)
    
    def _generate_title(self, commits: List[CommitInfo]) -> str:
        """
        커밋 정보를 바탕으로 블로그 제목을 생성합니다
        
        Args:
            commits: 커밋 정보 리스트
            
        Returns:
            생성된 제목
        """
        if not commits:
            return "오늘의 개발 일지"
        
        # 커밋 메시지들을 분석하여 제목 생성
        commit_messages = [commit.message for commit in commits]
        messages_text = "\n".join(commit_messages)
        
        prompt = f"""
다음 Git 커밋 메시지들을 분석하여 기술 블로그 포스트의 제목을 생성해주세요.
제목은 간결하고 명확해야 하며, 개발자가 작성한 것처럼 자연스러워야 합니다.

커밋 메시지들:
{messages_text}

제목만 한 줄로 출력해주세요. 따옴표나 특수문자는 사용하지 마세요.
"""
        
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 기술 블로그 작성을 도와주는 AI 어시스턴트입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            title = response.choices[0].message.content.strip()
            logger.info(f"블로그 제목 생성 완료: {title}")
            return title
            
        except Exception as e:
            logger.error(f"제목 생성 중 오류 발생: {e}")
            return "오늘의 개발 일지"
    
    def _generate_content(self, commit_summary: str) -> str:
        """
        커밋 정보를 바탕으로 블로그 본문을 생성합니다
        
        Args:
            commit_summary: 포맷팅된 커밋 정보
            
        Returns:
            생성된 블로그 본문
        """
        prompt = f"""
다음 Git 커밋 정보를 바탕으로 기술 블로그 포스트를 작성해주세요.

커밋 정보:
{commit_summary}

다음 형식으로 작성해주세요:

## ✨ 들어가며
오늘 어떤 기능을 개발했는지, 혹은 어떤 버그를 수정했는지 간략하게 소개하는 문단입니다.

## 📝 주요 변경 사항
- (관련 Git 커밋 해시) 변경된 핵심 로직이나 기능에 대해 서술합니다.
- 코드 블록을 사용해 실제 코드 변경점을 보여줍니다.

## 💡 구현 과정 및 배운 점
개발 과정에서 겪었던 어려움, 해결 방법, 새롭게 알게 된 점 등을 자유롭게 서술합니다.

## ✅ 마무리
다음 계획이나 소감을 짧게 남기는 문단입니다.

자연스럽고 읽기 쉬운 한국어로 작성해주세요. 기술적이면서도 친근한 톤을 유지해주세요.
"""
        
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 경험 많은 개발자이자 기술 블로그 작가입니다. Git 커밋 정보를 바탕으로 유익하고 읽기 쉬운 기술 블로그 포스트를 작성합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            logger.info("블로그 본문 생성 완료")
            return content
            
        except Exception as e:
            logger.error(f"본문 생성 중 오류 발생: {e}")
            return f"""
## ✨ 들어가며
오늘 Git 커밋 정보를 분석하여 블로그 포스트를 생성하려고 했지만, 내용 생성 중 오류가 발생했습니다.

## 📝 주요 변경 사항
{commit_summary}

## 💡 구현 과정 및 배운 점
AI를 활용한 블로그 자동 생성 시스템을 구축하는 과정에서 다양한 도전과제를 마주했습니다.

## ✅ 마무리
앞으로 더 나은 블로그 생성 시스템을 만들어보겠습니다.
"""
