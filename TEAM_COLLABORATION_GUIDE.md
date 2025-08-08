# 🚀 아마존-네이버 스마트스토어 프로젝트 팀 협업 가이드

## 📋 프로젝트 개요
완성된 아마존-네이버 스마트스토어 자동화 프로젝트를 팀원들과 공유하여 각자의 Claude Code에서 기능 확장/개선 작업을 진행하는 협업 시스템입니다.

## 🏗️ 프로젝트 구조
```
amazon-smartstore-automation/
├── amazon_smartstore_integrated.py    # 메인 GUI 프로그램
├── smartstore_uploader.py             # 스마트스토어 업로더
├── naver_smartstore_api.py            # 네이버 API 연동
├── git_slack_collaboration.py         # 협업 도구
├── requirements_collaboration.txt     # 협업용 의존성
├── .env.template                      # 환경변수 템플릿
└── README.md                          # 프로젝트 설명
```

## 🔧 팀원별 초기 설정

### 1️⃣ **GitHub Personal Access Token 생성**

1. **GitHub 로그인** → 우상단 프로필 아이콘 클릭
2. **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. **Generate new token (classic)** 클릭
4. **토큰 설정**:
   - Name: `Amazon Project Token`
   - Expiration: `90 days` (권장)
   - **필수 권한 선택**:
     - ☑️ **repo** (전체 선택)
     - ☑️ **workflow**
     - ☑️ **write:packages**
5. **Generate token** 클릭 후 **즉시 복사 저장** (다시 볼 수 없음)

### 2️⃣ **로컬 환경 설정**

**A. 저장소 클론**
```bash
# 터미널/명령프롬프트에서 실행
git clone https://github.com/your-org/amazon-smartstore-automation.git
cd amazon-smartstore-automation
```

**B. 가상환경 설정**
```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements_collaboration.txt
```

**C. 개인 환경변수 설정**
```bash
# .env.template을 복사하여 .env 파일 생성
copy .env.template .env    # Windows
cp .env.template .env      # Mac/Linux
```

**.env 파일 편집** (각자 개인 정보로 수정):
```bash
# 개인 GitHub 설정
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_github_username
GITHUB_EMAIL=your_email@example.com

# 공통 저장소 정보 (모두 동일)
GITHUB_REPO=amazon-smartstore-automation
GITHUB_REPO_URL=https://github.com/your-org/amazon-smartstore-automation.git

# 팀 Slack 설정 (팀장이 제공)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
SLACK_CHANNEL=#amazon-project
```

**D. Git 개인 설정**
```bash
git config user.name "본인이름"
git config user.email "본인이메일@example.com"
```

### 3️⃣ **연결 테스트**

```bash
# 협업 시스템 테스트
python git_slack_collaboration.py
# 메뉴에서 "1. 팀 상태 리포트 전송" 선택
```

성공하면 Slack 채널에 상태 리포트가 전송됩니다!

## 🚀 일상 협업 워크플로우

### 📝 **작업 시작 전 (매번 필수)**
```bash
# 1. 최신 코드 동기화
python -c "
from git_slack_collaboration import GitSlackCollaboration
collab = GitSlackCollaboration()
collab.sync_with_remote()
"

# 2. 가상환경 활성화
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
```

### 🔧 **기능 개발 워크플로우**

**A. 새 기능 개발 시**
```bash
# 1. 새 브랜치 생성
python -c "
from git_slack_collaboration import GitSlackCollaboration
collab = GitSlackCollaboration()
collab.create_branch_and_pr('feature/새기능명', '새 기능 설명')
"

# 2. Claude Code에서 개발 작업 진행
# 예: 이미지 최적화 기능 추가, UI 개선, API 연동 등

# 3. 작업 완료 후 커밋/푸시
python -c "
from git_slack_collaboration import GitSlackCollaboration
collab = GitSlackCollaboration()
collab.git_commit_and_push('이미지 최적화 기능 추가')
"
```

**B. 버그 수정 시**
```bash
# 직접 main 브랜치에서 작업
python -c "
from git_slack_collaboration import GitSlackCollaboration
collab = GitSlackCollaboration()
collab.git_commit_and_push('크롤링 속도 개선 버그 수정')
"
```

### 🎯 **Claude Code 활용 예시**

**1. GUI 개선 작업**
```python
# Claude Code에게 요청 예시:
# "amazon_smartstore_integrated.py의 UI를 더 사용자 친화적으로 개선해줘"
# "진행률 표시바를 추가하고 실시간 로그를 보여주는 기능을 넣어줘"
```

**2. 크롤링 성능 개선**
```python
# Claude Code에게 요청 예시:
# "크롤링 속도를 2배 향상시키고 메모리 사용량을 줄여줘"
# "멀티스레딩을 이용해서 동시에 여러 상품을 크롤링하도록 개선해줘"
```

**3. API 연동 확장**
```python
# Claude Code에게 요청 예시:
# "네이버 API 외에 쿠팡 API 연동도 추가해줘"
# "자동으로 상품 등록 상태를 모니터링하는 기능을 넣어줘"
```

### 📊 **정기 협업 활동**

**매일 오전 (권장)**
```bash
# 팀 상태 리포트 확인
python -c "
from git_slack_collaboration import GitSlackCollaboration
collab = GitSlackCollaboration()
collab.team_status_report()
"
```

**주간 회의 전**
```bash
# 개발 현황 요약 커밋
python -c "
from git_slack_collaboration import GitSlackCollaboration
collab = GitSlackCollaboration()
collab.git_commit_and_push('주간 개발 현황: 크롤링 안정성 개선, UI 업데이트 완료')
"
```

## 🎨 **추천 개발 영역별 분담**

### 👤 **팀원 A: Frontend & UI**
- GUI 개선 및 사용자 경험 향상
- 실시간 진행률 표시
- 에러 메시지 개선
- 설정 UI 추가

### 🔧 **팀원 B: Backend & Performance**  
- 크롤링 엔진 최적화
- 메모리 사용량 최적화
- 멀티스레딩/비동기 처리
- 캐시 시스템 구현

### 🌐 **팀원 C: API & Integration**
- 네이버 API 연동 완성
- 다른 쇼핑몰 API 추가
- 자동화 스케줄러 구현
- 모니터링 시스템

### 🧪 **팀원 D: QA & Testing**
- 자동 테스트 코드 작성
- 버그 발견 및 수정
- 성능 테스트
- 사용자 매뉴얼 작성

## 📱 **Slack 알림 시스템**

모든 Git 활동이 자동으로 팀 Slack 채널에 알림됩니다:

- ✅ **새 커밋 푸시**: `[팀원명]이 새 기능을 커밋했습니다`
- 🌿 **브랜치 생성**: `feature/이미지-최적화 브랜치가 생성되었습니다`  
- 🔄 **저장소 동기화**: `최신 코드로 동기화 완료`
- 📊 **상태 리포트**: `현재 프로젝트 진행 상황 리포트`

## ⚠️ **협업 규칙 & 주의사항**

### 🔒 **보안 규칙**
- ❌ Personal Access Token을 절대 공유하거나 코드에 포함하지 마세요
- ❌ .env 파일을 Git에 커밋하지 마세요 (.gitignore에 포함됨)
- ✅ 개인 정보는 .env 파일에만 저장하세요

### 🔄 **코드 관리 규칙**
- ✅ **작업 시작 전**: 항상 `sync_with_remote()` 실행
- ✅ **큰 기능 개발**: 별도 브랜치 생성 후 개발
- ✅ **작업 완료 후**: 즉시 커밋/푸시하여 팀과 공유
- ✅ **커밋 메시지**: 명확하고 구체적으로 작성

### 📝 **커밋 메시지 규칙**
```bash
# 좋은 예시
"크롤링 속도 20% 향상 - 비동기 처리 적용"
"GUI 진행률 표시 기능 추가"
"네이버 API 연동 완료 및 테스트 통과"

# 나쁜 예시  
"수정"
"업데이트"
"버그 픽스"
```

## 🆘 **문제 해결**

### Git 인증 오류
```bash
git config credential.helper store
# 다음 git 명령어 실행 시 토큰을 username으로, 비워둔 password로 입력
```

### Slack 알림 안됨
1. `.env` 파일의 `SLACK_WEBHOOK_URL` 확인
2. Slack 채널 권한 확인
3. 웹훅 URL 만료 여부 확인

### 패키지 설치 오류
```bash
# 개별 패키지 설치
pip install python-dotenv gitpython requests

# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements_collaboration.txt --force-reinstall
```

### Claude Code 연동 문제
1. 가상환경이 활성화되어 있는지 확인
2. 현재 디렉토리가 프로젝트 루트인지 확인
3. Python 경로가 올바른지 확인

## 🎯 **성공적인 팀 협업을 위한 팁**

### 💡 **효율적인 작업 분할**
- **작은 단위로 자주 커밋**: 큰 기능을 작은 단위로 나누어 개발
- **명확한 역할 분담**: 각자의 전문 영역에 집중
- **정기적인 동기화**: 매일 최신 코드로 업데이트

### 🗣️ **소통 방법**
- **Slack**: 개발 진행 상황 및 긴급 이슈
- **Git 커밋**: 코드 변경 사항 상세 설명
- **주간 회의**: 전체적인 방향성 및 우선순위 논의

### 🚀 **개발 속도 향상**
- **Claude Code 적극 활용**: 반복적인 코드 작성 자동화
- **템플릿 활용**: 공통 패턴을 템플릿으로 만들어 재사용
- **자동화 도구**: 테스트, 배포, 품질 검사 자동화

## 🎉 **프로젝트 확장 가능성**

현재 완성된 시스템을 기반으로 다음과 같은 확장이 가능합니다:

### 🛍️ **추가 쇼핑몰 지원**
- 쿠팡, 11번가, G마켓 등
- 해외 쇼핑몰 (eBay, Alibaba)

### 🤖 **AI 기능 강화**  
- 상품명 자동 최적화
- 카테고리 자동 분류
- 가격 경쟁력 분석

### 📊 **비즈니스 인텔리전스**
- 매출 분석 대시보드
- 트렌드 분석 리포트
- 재고 관리 시스템

---

**🎉 이제 모든 팀원이 Claude Code와 함께 완벽하게 협업할 수 있습니다!**

문제가 발생하면 팀 Slack 채널에서 서로 도움을 주고받으세요. 함께 만들어가는 프로젝트가 더욱 강력해질 것입니다! 💪