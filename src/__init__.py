"""
블로그 자동 생성 시스템

Git 커밋 로그를 분석하여 기술 블로그 포스트를 자동으로 생성하는 시스템입니다.
"""

__version__ = "1.0.0"
__author__ = "AI Blog Generator"
__description__ = "Git 커밋 로그 기반 자동 블로그 생성 시스템"

from .git_analyzer import GitAnalyzer, CommitInfo, FileChange
from .content_generator import ContentGenerator
from .post_formatter import PostFormatter
from .main import BlogGenerator

__all__ = [
    'GitAnalyzer',
    'CommitInfo', 
    'FileChange',
    'ContentGenerator',
    'PostFormatter',
    'BlogGenerator'
]
