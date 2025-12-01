# 🔐 보안 가이드 - API 키 및 인증 정보 관리

## ⚠️ 중요 사항

**절대로 API 키나 비밀번호를 코드에 직접 작성하지 마세요!**

하드코딩된 API 키는 심각한 보안 위협입니다:
- ✖️ GitHub에 업로드 시 누구나 볼 수 있음
- ✖️ 무단 사용으로 인한 비용 발생 위험
- ✖️ 계정 해킹 및 데이터 유출 가능
- ✖️ 서비스 이용 정지 가능

---

## ✅ 올바른 방법: 환경 변수 사용

### 1. `.env` 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```bash
# .env.template을 복사하여 시작
cp .env.template .env
```

### 2. 실제 API 키 입력

`.env` 파일을 열어 실제 API 키를 입력하세요:

```bash
# 네이버 스마트스토어 API 인증 정보
NAVER_CLIENT_ID=실제_클라이언트_아이디
NAVER_CLIENT_SECRET=실제_클라이언트_시크릿
NAVER_CUSTOMER_ID=실제_고객_아이디

# 아마존 API (선택사항)
AMAZON_ACCESS_KEY=실제_액세스_키
AMAZON_SECRET_KEY=실제_시크릿_키
```

### 3. 코드에서 안전하게 사용

```python
from config_loader import SecureConfigLoader

# 설정 로더 초기화
config = SecureConfigLoader()

# 안전하게 API 키 가져오기
naver_config = config.get_naver_config()

# API 클라이언트 초기화
api = NaverSmartStoreAPI(
    client_id=naver_config['client_id'],
    client_secret=naver_config['client_secret'],
    customer_id=naver_config['customer_id']
)
```

---

## ❌ 절대 하지 말아야 할 것

### 나쁜 예시 1: 하드코딩

```python
# ❌ 절대 하지 마세요!
api_key = "0dded578165b4c92a340970e94f94c5d.dNlQK1FhpZEVrN7o"
client_secret = "my_secret_key_12345"
```

### 나쁜 예시 2: JSON 파일에 저장 후 Git 커밋

```json
{
  "api_key": "actual_api_key",
  "secret": "actual_secret"
}
```

이런 파일을 Git에 커밋하면 영구적으로 이력에 남습니다!

---

## 🛡️ 보안 체크리스트

### 개발 시작 전

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] `.env.template`에는 플레이스홀더만 있고 실제 값은 없는지 확인
- [ ] 팀원들에게 환경 변수 사용 방법 공유

### 코드 작성 시

- [ ] API 키를 코드에 직접 작성하지 않았는지 확인
- [ ] `config_loader`를 사용하여 안전하게 로드했는지 확인
- [ ] 로그에 API 키가 노출되지 않는지 확인

### Git 커밋 전

- [ ] `git status`로 `.env` 파일이 포함되지 않았는지 확인
- [ ] 커밋할 파일에 API 키가 없는지 확인
- [ ] Pre-commit hook이 실행되는지 확인

### 배포 전

- [ ] 프로덕션 환경 변수가 별도로 설정되어 있는지 확인
- [ ] 개발/프로덕션 API 키가 분리되어 있는지 확인
- [ ] 환경 변수 백업이 안전한 곳에 저장되어 있는지 확인

---

## 🔧 도구 사용법

### config_loader.py 사용

#### 기본 사용법

```python
from config_loader import SecureConfigLoader

# 초기화
loader = SecureConfigLoader()

# 단일 환경 변수 가져오기
api_key = loader.get('NAVER_CLIENT_ID')

# 필수 환경 변수 (없으면 에러)
api_key = loader.get('NAVER_CLIENT_ID', required=True)

# 기본값 사용
timeout = loader.get('API_TIMEOUT', default='30')
```

#### 네이버 API 설정 가져오기

```python
try:
    naver_config = loader.get_naver_config()
    print(naver_config['client_id'])
except ValueError as e:
    print(f"설정 오류: {e}")
```

#### 설정 상태 확인

```python
loader.print_status()
```

출력 예시:
```
============================================================
🔐 환경 변수 설정 상태
============================================================

✅ 설정된 변수:
   • NAVER_CLIENT_ID: abc1****xyz9
   • NAVER_CLIENT_SECRET: sec1****key9
   • NAVER_CUSTOMER_ID: cus1****id99

✨ 모든 필수 환경 변수가 올바르게 설정되었습니다!
============================================================
```

### 하드코딩 감지 도구

프로젝트 전체에서 하드코딩된 API 키 검사:

```bash
python config_loader.py
```

또는 Python 코드에서:

```python
from config_loader import detect_hardcoded_credentials

issues = detect_hardcoded_credentials('my_file.py')
for issue in issues:
    print(f"Line {issue['line']}: {issue['type']}")
```

---

## 🚨 API 키가 노출된 경우

### 즉시 해야 할 일

1. **API 키 즉시 폐기**
   - 네이버 커머스 센터에서 기존 API 키 삭제
   - 아마존 AWS Console에서 액세스 키 비활성화

2. **새 API 키 발급**
   - 새로운 API 키 생성
   - `.env` 파일에만 저장

3. **Git 이력에서 제거** (이미 커밋된 경우)
   ```bash
   # 주의: 이 작업은 Git 이력을 재작성합니다
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # 강제 푸시
   git push origin --force --all
   ```

4. **팀원들에게 알림**
   - 모든 팀원이 새로운 API 키 사용하도록 안내
   - 보안 사고 공유 및 재발 방지 교육

---

## 📚 추가 리소스

### API 키 발급 방법

#### 네이버 커머스 API
1. [네이버 커머스 센터](https://commerce.naver.com/) 로그인
2. 설정 > API 연동 > 애플리케이션 등록
3. Client ID, Client Secret, Customer ID 확인

#### 아마존 Product Advertising API
1. [Amazon Associates](https://affiliate.amazon.com/) 계정 생성
2. Product Advertising API 신청
3. Access Key, Secret Key 발급

### 환경 변수 관리 도구

- **개발 환경**: `.env` 파일 + `config_loader.py`
- **프로덕션**:
  - AWS: AWS Secrets Manager, Parameter Store
  - Azure: Azure Key Vault
  - GCP: Secret Manager
  - Heroku: Config Vars
  - Docker: Docker Secrets

---

## 💡 모범 사례

### 1. 환경별 분리

```bash
.env.development  # 개발 환경
.env.staging      # 스테이징 환경
.env.production   # 프로덕션 환경
```

### 2. 팀 협업

- API 키는 안전한 채널로만 공유 (Slack 비공개 메시지, 암호화된 파일 등)
- `.env.template`에는 설명과 예시만 포함
- 팀 위키에 API 키 발급 방법 문서화

### 3. 정기적인 검토

- 분기마다 사용하지 않는 API 키 정리
- 6개월마다 API 키 순환 (rotation)
- 접근 권한 정기 검토

### 4. 로깅 시 주의

```python
# ❌ 나쁜 예
logger.info(f"API Key: {api_key}")

# ✅ 좋은 예
logger.info(f"API Key: {api_key[:4]}****{api_key[-4:]}")
```

---

## 🔒 추가 보안 강화

### Pre-commit Hook 설정

하드코딩된 API 키를 자동으로 감지:

```bash
# pre-commit hook 설치
chmod +x .git/hooks/pre-commit
```

### 2FA (2단계 인증) 활성화

- 네이버 계정 2FA 설정
- GitHub 계정 2FA 설정
- AWS 계정 2FA 설정

### IP 화이트리스트

가능한 경우 API 키를 특정 IP에서만 사용하도록 제한

---

## ❓ FAQ

### Q: `.env` 파일을 팀원과 공유해도 되나요?
A: **아니요!** 각자 자신의 `.env` 파일을 생성하고 개인 API 키를 사용해야 합니다.

### Q: 테스트용 API 키는 코드에 넣어도 되나요?
A: 테스트용이라도 환경 변수로 관리하세요. Mock/Stub을 사용하는 것이 더 좋습니다.

### Q: API 키가 실수로 커밋됐어요!
A: 즉시 API 키를 폐기하고 새로 발급하세요. Git 이력에서도 제거해야 합니다.

### Q: 여러 프로젝트에서 같은 API 키를 써도 되나요?
A: 가능하면 프로젝트별로 다른 API 키를 사용하는 것이 좋습니다.

---

## 📞 문의

보안 관련 문제 발견 시:
1. 즉시 팀 리더에게 보고
2. GitHub Security Advisory 작성
3. 영향받은 API 키 폐기

**보안은 모두의 책임입니다!** 🛡️

---

마지막 업데이트: 2025-12-01
