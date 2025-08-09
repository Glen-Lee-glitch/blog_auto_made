"""
블로그 자동 생성 시스템의 메인 실행 파일

이 스크립트는 Git 분석, 내용 생성, 포맷팅의 전체 프로세스를 조율하고 실행합니다.
"""

import logging
import os
import sys
import argparse
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.git_analyzer import GitAnalyzer
from src.content_generator import ContentGenerator
from src.post_formatter import PostFormatter

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blog_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BlogGenerator:
    """블로그 자동 생성 시스템의 메인 클래스"""
    
    def __init__(self, repo_path: str, output_dir: str = "./output"):
        """
        BlogGenerator 초기화
        
        Args:
            repo_path: 분석할 Git 리포지토리 경로
            output_dir: 출력 디렉토리 경로
        """
        self.repo_path = repo_path
        self.output_dir = output_dir
        
        # 컴포넌트 초기화
        self.git_analyzer = None
        self.content_generator = None
        self.post_formatter = None
        
        self._initialize_components()
    
    def _initialize_components(self) -> None:
        """시스템 컴포넌트들을 초기화합니다"""
        try:
            # Git 분석기 초기화
            self.git_analyzer = GitAnalyzer(self.repo_path)
            logger.info("Git 분석기 초기화 완료")
            
            # 내용 생성기 초기화
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.content_generator = ContentGenerator(api_key, model)
            logger.info("내용 생성기 초기화 완료")
            
            # 포스트 포맷터 초기화
            self.post_formatter = PostFormatter(self.output_dir)
            logger.info("포스트 포맷터 초기화 완료")
            
        except Exception as e:
            logger.error(f"컴포넌트 초기화 중 오류 발생: {e}")
            raise
    
    def generate_blog_post(self, days: int = 7, include_file_changes: bool = True) -> Optional[str]:
        """
        블로그 포스트를 생성합니다
        
        Args:
            days: 분석할 커밋의 기간 (일)
            include_file_changes: 파일 변경 상세 정보 포함 여부
            
        Returns:
            생성된 블로그 포스트 파일 경로
        """
        try:
            logger.info(f"블로그 포스트 생성 시작 (분석 기간: {days}일)")
            
            # 1. Git 커밋 분석
            commits = self.git_analyzer.get_recent_commits(days)
            if not commits:
                logger.warning(f"최근 {days}일간 커밋이 없습니다.")
                return None
            
            logger.info(f"{len(commits)}개의 커밋을 분석했습니다.")
            
            # 2. 파일 변경 상세 정보 수집 (선택사항)
            file_changes = []
            if include_file_changes and commits:
                # 가장 최근 커밋의 파일 변경사항만 분석
                latest_commit = commits[0]
                file_changes = self.git_analyzer.get_file_changes(latest_commit.hash)
                logger.info(f"{len(file_changes)}개의 파일 변경사항을 분석했습니다.")
            
            # 3. 블로그 내용 생성
            content_data = self.content_generator.generate_blog_content(commits, file_changes)
            logger.info("블로그 내용 생성 완료")
            
            # 4. 포스트 포맷팅
            formatted_post = self.post_formatter.format_blog_post(content_data)
            logger.info("포스트 포맷팅 완료")
            
            # 5. 파일 저장
            title = content_data.get('title', '오늘의 개발 일지')
            filename = self.post_formatter.generate_filename_from_title(title)
            filepath = self.post_formatter.save_blog_post(formatted_post, filename)
            
            logger.info(f"블로그 포스트 생성 완료: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"블로그 포스트 생성 중 오류 발생: {e}")
            return None
    
    def generate_multiple_posts(self, days_list: list, include_file_changes: bool = True) -> list:
        """
        여러 기간의 블로그 포스트를 생성합니다
        
        Args:
            days_list: 분석할 기간 리스트 (예: [1, 7, 30])
            include_file_changes: 파일 변경 상세 정보 포함 여부
            
        Returns:
            생성된 포스트 파일 경로 리스트
        """
        generated_posts = []
        
        for days in days_list:
            logger.info(f"{days}일간의 블로그 포스트 생성 시작")
            filepath = self.generate_blog_post(days, include_file_changes)
            if filepath:
                generated_posts.append(filepath)
        
        # 요약 파일 생성
        if generated_posts:
            self.post_formatter.create_summary_file(generated_posts)
        
        return generated_posts
    
    def get_repo_stats(self) -> dict:
        """
        리포지토리 통계 정보를 반환합니다
        
        Returns:
            리포지토리 통계 정보
        """
        return self.git_analyzer.get_repo_stats()


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Git 커밋 로그를 분석하여 블로그 포스트를 자동 생성합니다.")
    parser.add_argument("--repo-path", "-r", required=True, help="분석할 Git 리포지토리 경로")
    parser.add_argument("--output-dir", "-o", default="./output", help="출력 디렉토리 경로")
    parser.add_argument("--days", "-d", type=int, default=7, help="분석할 커밋의 기간 (일)")
    parser.add_argument("--no-file-changes", action="store_true", help="파일 변경 상세 정보 제외")
    parser.add_argument("--stats", action="store_true", help="리포지토리 통계만 출력")
    
    args = parser.parse_args()
    
    try:
        # BlogGenerator 초기화
        generator = BlogGenerator(args.repo_path, args.output_dir)
        
        # 통계만 출력하는 경우
        if args.stats:
            stats = generator.get_repo_stats()
            print("\n=== 리포지토리 통계 ===")
            print(f"총 커밋 수: {stats.get('total_commits', 0)}")
            print(f"브랜치: {', '.join(stats.get('branches', []))}")
            print(f"현재 브랜치: {stats.get('active_branch', 'unknown')}")
            last_commit = stats.get('last_commit', {})
            if last_commit:
                print(f"최근 커밋: {last_commit.get('hash', 'unknown')} - {last_commit.get('message', 'unknown')}")
            return
        
        # 블로그 포스트 생성
        include_file_changes = not args.no_file_changes
        filepath = generator.generate_blog_post(args.days, include_file_changes)
        
        if filepath:
            print(f"\n✅ 블로그 포스트 생성 완료!")
            print(f"📁 파일 위치: {filepath}")
            print(f"📊 분석 기간: 최근 {args.days}일")
            print(f"🔍 파일 변경 상세: {'포함' if include_file_changes else '제외'}")
        else:
            print("\n❌ 블로그 포스트 생성에 실패했습니다.")
            print("로그 파일을 확인해주세요: blog_generator.log")
    
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        print(f"\n❌ 오류가 발생했습니다: {e}")
        print("로그 파일을 확인해주세요: blog_generator.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
