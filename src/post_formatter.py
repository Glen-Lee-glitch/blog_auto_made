"""
생성된 블로그 내용을 최종 Markdown 형식으로 변환하는 모듈

이 모듈은 ContentGenerator에서 생성된 내용을 받아서
Rule에 정의된 형식에 맞는 완성된 Markdown 블로그 포스트로 변환합니다.
"""

import logging
import os
from typing import Dict, Optional
from datetime import datetime
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostFormatter:
    """블로그 포스트를 Markdown 형식으로 포맷팅하는 클래스"""
    
    def __init__(self, output_dir: str = "./output"):
        """
        PostFormatter 초기화
        
        Args:
            output_dir: 출력 디렉토리 경로
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self) -> None:
        """출력 디렉토리가 존재하는지 확인하고 없으면 생성"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"출력 디렉토리 생성: {self.output_dir}")
    
    def format_blog_post(self, content_data: Dict[str, str], 
                        include_metadata: bool = True) -> str:
        """
        블로그 내용을 완성된 Markdown 형식으로 변환합니다
        
        Args:
            content_data: ContentGenerator에서 생성된 내용 데이터
            include_metadata: 메타데이터 포함 여부
            
        Returns:
            완성된 Markdown 형식의 블로그 포스트
        """
        try:
            title = content_data.get('title', '오늘의 개발 일지')
            content = content_data.get('content', '')
            generated_at = content_data.get('generated_at', '')
            
            # 메타데이터 생성
            metadata = ""
            if include_metadata:
                metadata = self._generate_metadata(title, generated_at)
            
            # 본문 포맷팅
            formatted_content = self._format_content(content)
            
            # 최종 포스트 조합
            final_post = f"{metadata}\n\n{formatted_content}"
            
            logger.info("블로그 포스트 포맷팅 완료")
            return final_post
            
        except Exception as e:
            logger.error(f"포스트 포맷팅 중 오류 발생: {e}")
            return f"# 오늘의 개발 일지\n\n포스트 포맷팅 중 오류가 발생했습니다: {str(e)}"
    
    def _generate_metadata(self, title: str, generated_at: str) -> str:
        """
        블로그 포스트의 메타데이터를 생성합니다
        
        Args:
            title: 블로그 제목
            generated_at: 생성 시간
            
        Returns:
            메타데이터 문자열
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        metadata = f"""---
title: "{title}"
date: {current_time}
author: "AI 블로그 생성기"
categories: ["개발일지", "기술블로그"]
tags: ["git", "개발", "ai", "자동화"]
generated_at: {generated_at}
---

> 이 포스트는 Git 커밋 로그를 분석하여 AI가 자동으로 생성한 내용입니다.
"""
        return metadata
    
    def _format_content(self, content: str) -> str:
        """
        블로그 본문을 포맷팅합니다
        
        Args:
            content: 원본 내용
            
        Returns:
            포맷팅된 내용
        """
        # 제목이 이미 포함되어 있다면 제거
        content = re.sub(r'^#\s+.*?\n', '', content, count=1)
        
        # 코드 블록 포맷팅 개선
        content = self._improve_code_blocks(content)
        
        # 링크 포맷팅 개선
        content = self._improve_links(content)
        
        # 리스트 포맷팅 개선
        content = self._improve_lists(content)
        
        return content
    
    def _improve_code_blocks(self, content: str) -> str:
        """
        코드 블록의 포맷팅을 개선합니다
        
        Args:
            content: 원본 내용
            
        Returns:
            개선된 내용
        """
        # Git 커밋 해시를 코드 블록으로 감싸기
        content = re.sub(r'\(([a-f0-9]{8})\)', r'(`\1`)', content)
        
        # 파일 경로를 코드 블록으로 감싸기
        content = re.sub(r'`([^`]+\.(py|js|ts|java|cpp|h|md|txt))`', r'`\1`', content)
        
        return content
    
    def _improve_links(self, content: str) -> str:
        """
        링크 포맷팅을 개선합니다
        
        Args:
            content: 원본 내용
            
        Returns:
            개선된 내용
        """
        # GitHub 링크 패턴 감지 및 개선
        github_pattern = r'https://github\.com/([^/\s]+)/([^/\s]+)'
        content = re.sub(github_pattern, r'[GitHub 저장소](https://github.com/\1/\2)', content)
        
        return content
    
    def _improve_lists(self, content: str) -> str:
        """
        리스트 포맷팅을 개선합니다
        
        Args:
            content: 원본 내용
            
        Returns:
            개선된 내용
        """
        # 리스트 항목 간격 조정
        lines = content.split('\n')
        improved_lines = []
        
        for i, line in enumerate(lines):
            improved_lines.append(line)
            
            # 리스트 항목 다음에 빈 줄 추가
            if line.strip().startswith('- ') and i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('- '):
                    improved_lines.append('')
        
        return '\n'.join(improved_lines)
    
    def save_blog_post(self, content: str, filename: Optional[str] = None) -> str:
        """
        블로그 포스트를 파일로 저장합니다
        
        Args:
            content: 포맷팅된 블로그 포스트 내용
            filename: 저장할 파일명 (None인 경우 자동 생성)
            
        Returns:
            저장된 파일 경로
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"blog_post_{timestamp}.md"
            
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"블로그 포스트 저장 완료: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"파일 저장 중 오류 발생: {e}")
            raise
    
    def generate_filename_from_title(self, title: str) -> str:
        """
        제목을 바탕으로 파일명을 생성합니다
        
        Args:
            title: 블로그 제목
            
        Returns:
            생성된 파일명
        """
        # 특수문자 제거 및 공백을 언더스코어로 변경
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '_', filename)
        filename = filename.lower().strip('_')
        
        # 날짜 추가
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{date_str}_{filename}.md"
        
        return filename
    
    def create_summary_file(self, posts: list) -> str:
        """
        여러 블로그 포스트의 요약 파일을 생성합니다
        
        Args:
            posts: 블로그 포스트 정보 리스트
            
        Returns:
            생성된 요약 파일 경로
        """
        try:
            summary_content = "# 블로그 포스트 목록\n\n"
            summary_content += f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for i, post in enumerate(posts, 1):
                title = post.get('title', f'포스트 {i}')
                filename = post.get('filename', f'post_{i}.md')
                generated_at = post.get('generated_at', '')
                
                summary_content += f"## {i}. {title}\n"
                summary_content += f"- 파일: `{filename}`\n"
                if generated_at:
                    summary_content += f"- 생성시간: {generated_at}\n"
                summary_content += "\n"
            
            summary_filepath = os.path.join(self.output_dir, "posts_summary.md")
            
            with open(summary_filepath, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"요약 파일 생성 완료: {summary_filepath}")
            return summary_filepath
            
        except Exception as e:
            logger.error(f"요약 파일 생성 중 오류 발생: {e}")
            raise
