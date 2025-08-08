#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git & Slack 협업 시스템
아마존-네이버 스마트스토어 프로젝트 팀 협업을 위한 통합 도구
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import logging

class GitSlackCollaboration:
    def __init__(self):
        """협업 시스템 초기화"""
        # .env 파일 로드
        load_dotenv()
        
        # 환경 변수 설정
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO')
        self.github_repo_url = os.getenv('GITHUB_REPO_URL')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#general')
        self.team_name = os.getenv('TEAM_NAME', 'Amazon_Team')
        self.project_name = os.getenv('PROJECT_NAME', 'Amazon_Project')
        
        # Git 사용자 정보
        self.git_username = os.getenv('GITHUB_USERNAME', 'Unknown')
        self.git_email = os.getenv('GITHUB_EMAIL', 'unknown@example.com')
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._validate_config()

    def _validate_config(self):
        """설정 검증"""
        missing = []
        if not self.github_token:
            missing.append('GITHUB_TOKEN')
        if not self.slack_webhook:
            missing.append('SLACK_WEBHOOK_URL')
        
        if missing:
            self.logger.error(f"필수 환경변수가 설정되지 않음: {', '.join(missing)}")
            self.logger.info(".env 파일을 확인하고 필요한 값들을 설정해주세요.")

    def _run_git_command(self, command):
        """Git 명령어 실행"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8'
            )
            if result.returncode != 0:
                self.logger.error(f"Git 명령어 실행 실패: {command}")
                self.logger.error(f"에러: {result.stderr}")
                return None
            return result.stdout.strip()
        except Exception as e:
            self.logger.error(f"Git 명령어 실행 중 오류: {e}")
            return None

    def send_slack_message(self, message, color="good"):
        """Slack 메시지 전송"""
        if not self.slack_webhook:
            self.logger.warning("Slack 웹훅이 설정되지 않아 메시지를 전송하지 않습니다.")
            return False
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        payload = {
            "channel": self.slack_channel,
            "username": f"{self.project_name}-Bot",
            "icon_emoji": ":robot_face:",
            "attachments": [{
                "color": color,
                "fields": [{
                    "title": f"🚀 {self.team_name} 활동 알림",
                    "value": f"{message}\n\n⏰ 시간: {timestamp}\n👤 팀원: {self.git_username}",
                    "short": False
                }]
            }]
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info("Slack 메시지 전송 성공")
                return True
            else:
                self.logger.error(f"Slack 메시지 전송 실패: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Slack 메시지 전송 중 오류: {e}")
            return False

    def git_commit_and_push(self, commit_message, branch="main"):
        """Git 커밋 및 푸시"""
        self.logger.info(f"Git 커밋 및 푸시 시작: {commit_message}")
        
        # Git 사용자 설정
        self._run_git_command(f'git config user.name "{self.git_username}"')
        self._run_git_command(f'git config user.email "{self.git_email}"')
        
        # 변경사항 확인
        status = self._run_git_command("git status --porcelain")
        if not status:
            self.logger.info("커밋할 변경사항이 없습니다.")
            return False
        
        # 스테이징
        self._run_git_command("git add .")
        
        # 커밋
        commit_result = self._run_git_command(f'git commit -m "{commit_message}"')
        if not commit_result:
            return False
        
        # 푸시
        push_result = self._run_git_command(f"git push origin {branch}")
        if push_result is not None:
            # Slack 알림
            self.send_slack_message(
                f"✅ **새 커밋이 푸시되었습니다!**\n"
                f"📝 메시지: {commit_message}\n"
                f"🌿 브랜치: {branch}\n"
                f"📊 저장소: {self.github_repo}",
                "good"
            )
            self.logger.info("Git 커밋 및 푸시 완료")
            return True
        
        return False

    def sync_with_remote(self, branch="main"):
        """원격 저장소와 동기화"""
        self.logger.info("원격 저장소와 동기화 중...")
        
        # 페치
        fetch_result = self._run_git_command("git fetch origin")
        if fetch_result is None:
            return False
        
        # 풀
        pull_result = self._run_git_command(f"git pull origin {branch}")
        if pull_result is not None:
            # Slack 알림
            self.send_slack_message(
                f"🔄 **저장소 동기화 완료**\n"
                f"🌿 브랜치: {branch}\n"
                f"📊 저장소: {self.github_repo}",
                "warning"
            )
            self.logger.info("동기화 완료")
            return True
        
        return False

    def create_branch_and_pr(self, branch_name, description):
        """새 브랜치 생성 및 PR 준비"""
        self.logger.info(f"새 브랜치 생성: {branch_name}")
        
        # 브랜치 생성 및 체크아웃
        create_result = self._run_git_command(f"git checkout -b {branch_name}")
        if create_result is not None:
            # Slack 알림
            self.send_slack_message(
                f"🌿 **새 브랜치가 생성되었습니다!**\n"
                f"📝 브랜치명: {branch_name}\n"
                f"📄 설명: {description}\n"
                f"📊 저장소: {self.github_repo}",
                "warning"
            )
            self.logger.info(f"브랜치 {branch_name} 생성 완료")
            return True
        
        return False

    def team_status_report(self):
        """팀 상태 리포트"""
        self.logger.info("팀 상태 리포트 생성 중...")
        
        # Git 정보 수집
        current_branch = self._run_git_command("git branch --show-current") or "unknown"
        latest_commit = self._run_git_command("git log -1 --pretty=format:'%h - %s (%cr) <%an>'") or "정보 없음"
        file_count = len([f for f in os.listdir('.') if os.path.isfile(f)])
        
        report = (
            f"📊 **{self.team_name} 상태 리포트**\n\n"
            f"🏗️ 프로젝트: {self.project_name}\n"
            f"🌿 현재 브랜치: {current_branch}\n"
            f"📝 최근 커밋: {latest_commit}\n"
            f"📁 파일 개수: {file_count}개\n"
            f"👤 리포트 생성자: {self.git_username}"
        )
        
        self.send_slack_message(report, "good")
        self.logger.info("팀 상태 리포트 전송 완료")
        return True

    def quick_commit_push(self, feature_description):
        """빠른 커밋/푸시 (GUI에서 작업한 후)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        commit_message = f"[{timestamp}] {feature_description}"
        return self.git_commit_and_push(commit_message)

    def setup_git_hooks(self):
        """Git 훅 설정 (선택사항)"""
        hooks_dir = ".git/hooks"
        if not os.path.exists(hooks_dir):
            os.makedirs(hooks_dir)
        
        # pre-commit 훅 생성
        pre_commit_hook = os.path.join(hooks_dir, "pre-commit")
        with open(pre_commit_hook, 'w', encoding='utf-8') as f:
            f.write("""#!/bin/bash
echo "Pre-commit 검사 실행 중..."
# 파이썬 구문 검사
python -m py_compile *.py
if [ $? -ne 0 ]; then
    echo "파이썬 구문 오류가 발견되었습니다. 커밋을 중단합니다."
    exit 1
fi
echo "Pre-commit 검사 통과"
""")
        
        # 실행 권한 부여 (Windows에서는 무시됨)
        try:
            os.chmod(pre_commit_hook, 0o755)
        except:
            pass
        
        self.logger.info("Git 훅 설정 완료")


def main():
    """메인 함수 - 테스트 및 예제"""
    print("🚀 Git & Slack 협업 시스템")
    print("=" * 50)
    
    collab = GitSlackCollaboration()
    
    # 대화형 메뉴
    while True:
        print("\n선택하세요:")
        print("1. 팀 상태 리포트 전송")
        print("2. 작업 커밋 및 푸시")
        print("3. 원격 저장소와 동기화")
        print("4. 새 브랜치 생성")
        print("5. 종료")
        
        choice = input("\n번호를 입력하세요 (1-5): ").strip()
        
        if choice == "1":
            collab.team_status_report()
        elif choice == "2":
            message = input("커밋 메시지를 입력하세요: ").strip()
            if message:
                collab.git_commit_and_push(message)
        elif choice == "3":
            collab.sync_with_remote()
        elif choice == "4":
            branch = input("브랜치명을 입력하세요: ").strip()
            desc = input("브랜치 설명을 입력하세요: ").strip()
            if branch:
                collab.create_branch_and_pr(branch, desc)
        elif choice == "5":
            print("협업 시스템을 종료합니다.")
            break
        else:
            print("올바른 번호를 선택해주세요.")


if __name__ == "__main__":
    main()