"""
Git 커밋 로그를 분석하고 변경사항을 추출하는 모듈

이 모듈은 GitPython을 사용하여 리포지토리의 커밋 히스토리를 분석하고,
변경된 파일들과 커밋 메시지를 추출합니다.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from git import Repo, Commit, Diff
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CommitInfo:
    """커밋 정보를 담는 데이터 클래스"""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    additions: int
    deletions: int


@dataclass
class FileChange:
    """파일 변경 정보를 담는 데이터 클래스"""
    file_path: str
    change_type: str  # 'A' (추가), 'M' (수정), 'D' (삭제)
    additions: int
    deletions: int
    diff_content: str


class GitAnalyzer:
    """Git 리포지토리를 분석하는 클래스"""
    
    def __init__(self, repo_path: str):
        """
        GitAnalyzer 초기화
        
        Args:
            repo_path: Git 리포지토리 경로
        """
        self.repo_path = repo_path
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self) -> None:
        """Git 리포지토리 초기화"""
        try:
            self.repo = Repo(self.repo_path)
            logger.info(f"Git 리포지토리 초기화 완료: {self.repo_path}")
        except Exception as e:
            logger.error(f"Git 리포지토리 초기화 실패: {e}")
            raise
    
    def get_recent_commits(self, days: int = 7) -> List[CommitInfo]:
        """
        최근 N일간의 커밋들을 가져옵니다
        
        Args:
            days: 조회할 일수 (기본값: 7일)
            
        Returns:
            최근 커밋 정보 리스트
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            commits = []
            for commit in self.repo.iter_commits('main'):
                commit_date = datetime.fromtimestamp(commit.committed_date)
                
                if commit_date < start_date:
                    break
                
                commit_info = self._extract_commit_info(commit)
                commits.append(commit_info)
            
            logger.info(f"최근 {days}일간 {len(commits)}개의 커밋을 찾았습니다")
            return commits
            
        except Exception as e:
            logger.error(f"커밋 조회 중 오류 발생: {e}")
            return []
    
    def _extract_commit_info(self, commit: Commit) -> CommitInfo:
        """
        커밋 객체에서 정보를 추출합니다
        
        Args:
            commit: Git 커밋 객체
            
        Returns:
            추출된 커밋 정보
        """
        # 변경된 파일 목록
        files_changed = []
        additions = 0
        deletions = 0
        
        if commit.parents:
            # 부모 커밋과의 차이점 분석
            diff = commit.diff(commit.parents[0])
            for change in diff:
                files_changed.append(change.a_path or change.b_path)
                # stats가 없는 경우 0으로 처리
                try:
                    additions += change.stats.get('insertions', 0)
                    deletions += change.stats.get('deletions', 0)
                except AttributeError:
                    # stats 속성이 없는 경우
                    pass
        else:
            # 최초 커밋인 경우
            for file_path in commit.stats.files.keys():
                files_changed.append(file_path)
            # stats.files.values()는 dict이므로 안전하게 처리
            try:
                additions = sum(commit.stats.files.values())
            except TypeError:
                additions = 0
        
        return CommitInfo(
            hash=commit.hexsha[:8],
            author=commit.author.name,
            date=datetime.fromtimestamp(commit.committed_date),
            message=commit.message.strip(),
            files_changed=files_changed,
            additions=additions,
            deletions=deletions
        )
    
    def get_file_changes(self, commit_hash: str) -> List[FileChange]:
        """
        특정 커밋의 파일 변경사항을 상세히 분석합니다
        
        Args:
            commit_hash: 커밋 해시
            
        Returns:
            파일 변경 정보 리스트
        """
        try:
            commit = self.repo.commit(commit_hash)
            changes = []
            
            if commit.parents:
                diff = commit.diff(commit.parents[0])
                for change in diff:
                    file_change = self._extract_file_change(change)
                    if file_change:
                        changes.append(file_change)
            
            return changes
            
        except Exception as e:
            logger.error(f"파일 변경사항 분석 중 오류 발생: {e}")
            return []
    
    def _extract_file_change(self, diff: Diff) -> Optional[FileChange]:
        """
        diff 객체에서 파일 변경 정보를 추출합니다
        
        Args:
            diff: Git diff 객체
            
        Returns:
            파일 변경 정보
        """
        try:
            file_path = diff.a_path or diff.b_path
            if not file_path:
                return None
            
            # 변경 타입 결정
            if diff.new_file:
                change_type = 'A'  # 추가
            elif diff.deleted_file:
                change_type = 'D'  # 삭제
            else:
                change_type = 'M'  # 수정
            
            # diff 내용 추출
            diff_content = diff.diff.decode('utf-8', errors='ignore')
            
            # stats 정보 추출 (안전하게)
            try:
                additions = diff.stats.get('insertions', 0)
                deletions = diff.stats.get('deletions', 0)
            except AttributeError:
                additions = 0
                deletions = 0
            
            return FileChange(
                file_path=file_path,
                change_type=change_type,
                additions=additions,
                deletions=deletions,
                diff_content=diff_content
            )
            
        except Exception as e:
            logger.error(f"파일 변경 정보 추출 중 오류: {e}")
            return None
    
    def get_repo_stats(self) -> Dict[str, any]:
        """
        리포지토리 전체 통계를 가져옵니다
        
        Returns:
            리포지토리 통계 정보
        """
        try:
            stats = {
                'total_commits': len(list(self.repo.iter_commits())),
                'branches': [branch.name for branch in self.repo.branches],
                'active_branch': self.repo.active_branch.name,
                'last_commit': {
                    'hash': self.repo.head.commit.hexsha[:8],
                    'message': self.repo.head.commit.message.strip(),
                    'date': datetime.fromtimestamp(self.repo.head.commit.committed_date)
                }
            }
            return stats
            
        except Exception as e:
            logger.error(f"리포지토리 통계 조회 중 오류 발생: {e}")
            return {}
