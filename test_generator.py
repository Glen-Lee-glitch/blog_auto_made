#!/usr/bin/env python3
"""
블로그 생성기 테스트 스크립트

이 스크립트는 블로그 생성 시스템의 기본 기능을 테스트합니다.
"""

import os
import sys
from src.main import BlogGenerator

def test_blog_generator():
    """블로그 생성기를 테스트합니다"""
    print("🚀 블로그 생성기 테스트 시작")
    
    # 현재 디렉토리를 Git 리포지토리로 사용
    repo_path = "."
    output_dir = "./test_output"
    
    try:
        # BlogGenerator 초기화
        print("📦 BlogGenerator 초기화 중...")
        generator = BlogGenerator(repo_path, output_dir)
        print("✅ 초기화 완료")
        
        # 리포지토리 통계 출력
        print("\n📊 리포지토리 통계:")
        stats = generator.get_repo_stats()
        print(f"  - 총 커밋 수: {stats.get('total_commits', 0)}")
        print(f"  - 브랜치: {', '.join(stats.get('branches', []))}")
        print(f"  - 현재 브랜치: {stats.get('active_branch', 'unknown')}")
        
        # 블로그 포스트 생성 테스트
        print("\n📝 블로그 포스트 생성 테스트...")
        filepath = generator.generate_blog_post(days=7, include_file_changes=True)
        
        if filepath:
            print(f"✅ 블로그 포스트 생성 성공!")
            print(f"📁 파일 위치: {filepath}")
            
            # 생성된 파일 내용 미리보기
            print("\n📖 생성된 파일 미리보기:")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 처음 500자만 출력
                    preview = content[:500] + "..." if len(content) > 500 else content
                    print(preview)
            except Exception as e:
                print(f"파일 읽기 오류: {e}")
        else:
            print("❌ 블로그 포스트 생성 실패")
            return False
        
        print("\n🎉 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = test_blog_generator()
    sys.exit(0 if success else 1)
