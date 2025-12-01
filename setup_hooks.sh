#!/bin/bash
# Pre-commit hook 설치 스크립트

echo "🔧 Git pre-commit hook 설치 중..."

# Git 저장소인지 확인
if [ ! -d ".git" ]; then
    echo "❌ Git 저장소가 아닙니다. git init을 먼저 실행하세요."
    exit 1
fi

# hooks 디렉토리 생성
mkdir -p .git/hooks

# pre-commit 파일 복사
if [ -f "pre-commit" ]; then
    cp pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo "✅ Pre-commit hook이 설치되었습니다!"
    echo ""
    echo "📋 이제 git commit 시 자동으로 하드코딩된 API 키를 검사합니다."
    echo ""
else
    echo "❌ pre-commit 파일을 찾을 수 없습니다."
    exit 1
fi

# 테스트
echo "🧪 Hook 테스트 중..."
.git/hooks/pre-commit
if [ $? -eq 0 ]; then
    echo "✅ Hook이 정상적으로 작동합니다!"
else
    echo "⚠️  Hook 실행 중 문제가 있을 수 있습니다."
    echo "   Python3이 설치되어 있는지 확인하세요."
fi

echo ""
echo "✨ 설정 완료!"
