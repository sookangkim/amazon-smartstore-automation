#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
안전한 환경 변수 로더
API 키와 같은 민감한 정보를 환경 변수에서 안전하게 로드합니다.

작성일: 2025-12-01
버전: v1.0
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecureConfigLoader:
    """안전한 설정 로더 클래스"""

    def __init__(self, env_file: str = ".env"):
        """
        초기화

        Args:
            env_file: 환경 변수 파일 경로 (기본값: .env)
        """
        self.env_file = Path(env_file)
        self.config = {}
        self._load_env_file()

    def _load_env_file(self):
        """
        .env 파일에서 환경 변수 로드
        python-dotenv 패키지가 없어도 작동하는 간단한 구현
        """
        if not self.env_file.exists():
            logger.warning(f"환경 변수 파일을 찾을 수 없습니다: {self.env_file}")
            logger.warning(f".env.template을 복사하여 {self.env_file}을 생성하고 실제 값을 입력하세요")
            return

        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()

                    # 빈 줄이나 주석은 건너뛰기
                    if not line or line.startswith('#'):
                        continue

                    # KEY=VALUE 형식 파싱
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # 환경 변수로 설정 (기존 환경 변수가 우선)
                        if key not in os.environ:
                            os.environ[key] = value

                        self.config[key] = os.environ.get(key, value)

            logger.info(f"환경 변수 파일 로드 완료: {self.env_file}")

        except Exception as e:
            logger.error(f"환경 변수 파일 로드 실패: {e}")

    def get(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """
        환경 변수 값 가져오기

        Args:
            key: 환경 변수 키
            default: 기본값
            required: 필수 여부 (True일 경우 값이 없으면 에러)

        Returns:
            환경 변수 값

        Raises:
            ValueError: required=True이고 값이 없을 때
        """
        value = os.environ.get(key, self.config.get(key, default))

        if required and not value:
            raise ValueError(
                f"필수 환경 변수 '{key}'가 설정되지 않았습니다. "
                f".env 파일에서 설정하거나 환경 변수로 설정해주세요."
            )

        # 보안: 플레이스홀더 값 감지
        if value and self._is_placeholder(value):
            if required:
                raise ValueError(
                    f"환경 변수 '{key}'에 실제 값을 입력해주세요. "
                    f"현재 값은 플레이스홀더입니다: {value}"
                )
            logger.warning(f"환경 변수 '{key}'에 플레이스홀더 값이 사용되고 있습니다")
            return None

        return value

    def _is_placeholder(self, value: str) -> bool:
        """플레이스홀더 값인지 확인"""
        placeholders = [
            'your_', 'YOUR_', 'replace_', 'REPLACE_',
            'example', 'EXAMPLE', 'placeholder', 'PLACEHOLDER',
            'xxx', 'XXX', 'yyy', 'YYY',
            'changeme', 'CHANGEME', 'todo', 'TODO'
        ]

        value_lower = value.lower()
        return any(ph.lower() in value_lower for ph in placeholders)

    def get_naver_config(self) -> Dict[str, str]:
        """
        네이버 스마트스토어 API 설정 가져오기

        Returns:
            네이버 API 설정 딕셔너리

        Raises:
            ValueError: 필수 값이 없을 때
        """
        return {
            'client_id': self.get('NAVER_CLIENT_ID', required=True),
            'client_secret': self.get('NAVER_CLIENT_SECRET', required=True),
            'customer_id': self.get('NAVER_CUSTOMER_ID', required=True)
        }

    def get_amazon_config(self) -> Optional[Dict[str, str]]:
        """
        아마존 API 설정 가져오기 (선택사항)

        Returns:
            아마존 API 설정 딕셔너리 또는 None
        """
        access_key = self.get('AMAZON_ACCESS_KEY')
        secret_key = self.get('AMAZON_SECRET_KEY')

        if access_key and secret_key:
            return {
                'access_key': access_key,
                'secret_key': secret_key,
                'associate_tag': self.get('AMAZON_ASSOCIATE_TAG', '')
            }

        return None

    def validate_all(self) -> Dict[str, Any]:
        """
        모든 필수 설정 검증

        Returns:
            검증 결과 딕셔너리
        """
        results = {
            'valid': True,
            'missing': [],
            'placeholders': [],
            'configured': []
        }

        # 필수 환경 변수 목록
        required_vars = [
            'NAVER_CLIENT_ID',
            'NAVER_CLIENT_SECRET',
            'NAVER_CUSTOMER_ID'
        ]

        for var in required_vars:
            value = self.get(var)

            if not value:
                results['valid'] = False
                results['missing'].append(var)
            elif self._is_placeholder(value):
                results['valid'] = False
                results['placeholders'].append(var)
            else:
                results['configured'].append(var)

        return results

    def print_status(self):
        """설정 상태 출력"""
        print("\n" + "="*60)
        print("🔐 환경 변수 설정 상태")
        print("="*60)

        results = self.validate_all()

        if results['configured']:
            print("\n✅ 설정된 변수:")
            for var in results['configured']:
                # 보안: 실제 값은 일부만 표시
                value = self.get(var)
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                print(f"   • {var}: {masked_value}")

        if results['missing']:
            print("\n❌ 누락된 변수:")
            for var in results['missing']:
                print(f"   • {var}")

        if results['placeholders']:
            print("\n⚠️  플레이스홀더 값이 사용된 변수:")
            for var in results['placeholders']:
                print(f"   • {var}")

        if results['valid']:
            print("\n✨ 모든 필수 환경 변수가 올바르게 설정되었습니다!")
        else:
            print("\n⚠️  일부 환경 변수를 설정해야 합니다.")
            print("   .env 파일을 확인하고 실제 값을 입력해주세요.")

        print("="*60 + "\n")


def detect_hardcoded_credentials(file_path: str) -> list:
    """
    파일에서 하드코딩된 API 키 패턴 감지

    Args:
        file_path: 검사할 파일 경로

    Returns:
        발견된 의심스러운 패턴 리스트
    """
    import re

    suspicious_patterns = []

    # 의심스러운 패턴들
    patterns = [
        (r'api[_-]?key\s*=\s*["\']([^"\']{20,})["\']', 'API Key'),
        (r'secret[_-]?key\s*=\s*["\']([^"\']{20,})["\']', 'Secret Key'),
        (r'access[_-]?token\s*=\s*["\']([^"\']{20,})["\']', 'Access Token'),
        (r'client[_-]?secret\s*=\s*["\']([^"\']{20,})["\']', 'Client Secret'),
        (r'password\s*=\s*["\']([^"\']{8,})["\']', 'Password'),
        (r'bearer\s+([a-zA-Z0-9_-]{20,})', 'Bearer Token'),
        (r'[a-f0-9]{32,}', 'Potential Secret (Hex)'),
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            for pattern, name in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 플레이스홀더는 제외
                    matched_text = match.group(0)
                    if not any(ph in matched_text.lower() for ph in ['your_', 'example', 'placeholder', 'xxx']):
                        suspicious_patterns.append({
                            'type': name,
                            'pattern': matched_text[:50] + '...' if len(matched_text) > 50 else matched_text,
                            'line': content[:match.start()].count('\n') + 1
                        })

    except Exception as e:
        logger.error(f"파일 검사 실패 {file_path}: {e}")

    return suspicious_patterns


def main():
    """테스트 및 데모"""
    print("🔐 안전한 환경 변수 로더 데모\n")

    # 설정 로더 초기화
    loader = SecureConfigLoader()

    # 상태 출력
    loader.print_status()

    # 설정 값 가져오기 예제
    try:
        print("📝 네이버 API 설정 가져오기 시도...")
        naver_config = loader.get_naver_config()
        print("✅ 네이버 API 설정이 올바르게 로드되었습니다!\n")
    except ValueError as e:
        print(f"❌ {e}\n")

    # 파일 검사 예제
    print("🔍 Python 파일에서 하드코딩된 인증 정보 검사...")
    python_files = Path('.').glob('**/*.py')

    total_issues = 0
    for py_file in python_files:
        if '.git' in str(py_file) or '__pycache__' in str(py_file):
            continue

        issues = detect_hardcoded_credentials(str(py_file))
        if issues:
            print(f"\n⚠️  {py_file}:")
            for issue in issues:
                print(f"   Line {issue['line']}: {issue['type']} - {issue['pattern']}")
                total_issues += 1

    if total_issues == 0:
        print("✅ 하드코딩된 인증 정보가 발견되지 않았습니다!\n")
    else:
        print(f"\n⚠️  총 {total_issues}개의 잠재적 보안 문제가 발견되었습니다.\n")


if __name__ == "__main__":
    main()
