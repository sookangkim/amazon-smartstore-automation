# GLM AI 사용 가이드

GLM (General Language Model)은 중국 Zhipu AI에서 개발한 강력한 AI 언어 모델입니다. 이 가이드는 프로젝트에서 GLM을 활용하는 방법을 설명합니다.

## 📋 목차
1. [설치 및 설정](#설치-및-설정)
2. [기본 사용법](#기본-사용법)
3. [주요 기능](#주요-기능)
4. [실전 예제](#실전-예제)
5. [문제 해결](#문제-해결)

---

## 🚀 설치 및 설정

### 1단계: 패키지 설치

```bash
pip install -r requirements.txt
```

### 2단계: API 키 발급

1. [Zhipu AI 플랫폼](https://open.bigmodel.cn/)에 가입
2. 대시보드에서 API 키 생성
3. API 키 복사

### 3단계: 환경 변수 설정

`.env` 파일을 생성하고 다음 내용 추가:

```env
GLM_API_KEY=your_api_key_here
```

---

## 💡 기본 사용법

### 대화형 모드

가장 간단한 방법은 대화형 인터페이스를 사용하는 것입니다:

```bash
python glm_interaction.py
```

실행하면 다음과 같은 화면이 나타납니다:

```
============================================================
GLM AI 대화 시스템
============================================================
명령어:
  - 'exit' 또는 'quit': 종료
  - 'clear': 대화 히스토리 초기화
  - 'history': 대화 히스토리 보기
  - 'stream on/off': 스트리밍 모드 전환
============================================================

GLM과 대화를 시작합니다. 무엇이든 물어보세요!

당신:
```

### Python 코드에서 사용

```python
from glm_interaction import GLMInteraction

# GLM 클라이언트 초기화
glm = GLMInteraction()

# 간단한 대화
response = glm.chat("안녕하세요!")
print(response)
```

---

## 🎯 주요 기능

### 1. 기본 대화

```python
glm = GLMInteraction()
response = glm.chat("한국의 수도는 어디인가요?")
```

### 2. 스트리밍 모드

실시간으로 응답을 받아보세요:

```python
response = glm.chat("긴 이야기를 들려주세요.", stream=True)
```

### 3. 상품 분석

아마존 상품의 한국 시장 적합성을 분석:

```python
product_info = {
    "title": "CeraVe Moisturizing Cream",
    "price": 19.99,
    "category": "Beauty & Personal Care",
    "rating": 4.7,
    "review_count": 98543
}

analysis = glm.analyze_product(product_info)
print(analysis)
```

### 4. 번역

영어 상품 정보를 한국어로 번역:

```python
product = {
    "title": "Apple AirPods Pro (2nd Generation)",
    "description": "Active Noise Cancellation..."
}

translated = glm.translate_product(product)
print(translated['title'])
print(translated['description'])
```

### 5. 태그 생성

SEO 최적화를 위한 검색 태그 자동 생성:

```python
tags = glm.generate_product_tags("무선 블루투스 이어폰")
print(tags)  # ['블루투스이어폰', '무선이어폰', ...]
```

### 6. 대화 히스토리 관리

```python
# 대화 히스토리 보기
history = glm.get_history()

# 대화 히스토리 초기화
glm.clear_history()
```

---

## 📚 실전 예제

### 예제 1: 상품 수익성 분석

```python
from glm_interaction import GLMInteraction

glm = GLMInteraction()

product = {
    "title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
    "price": 89.99,
    "category": "Home & Kitchen",
    "rating": 4.6,
    "review_count": 125000
}

print("상품 분석 중...")
analysis = glm.analyze_product(product)
print(analysis)
```

### 예제 2: 자동 번역 및 태그 생성

```python
from glm_interaction import GLMInteraction

glm = GLMInteraction()

# 영어 상품 정보
product = {
    "title": "Wireless Gaming Mouse with RGB Lighting",
    "description": "High precision optical sensor, customizable buttons"
}

# 번역
translated = glm.translate_product(product)
korean_title = translated['title']

# 태그 생성
tags = glm.generate_product_tags(korean_title)

print(f"번역된 제목: {korean_title}")
print(f"태그: {', '.join(tags)}")
```

### 예제 3: 비즈니스 전략 상담

```python
from glm_interaction import GLMInteraction

glm = GLMInteraction()

questions = [
    "아마존 구매대행 사업에서 가장 중요한 것은?",
    "경쟁업체와 차별화하는 방법은?",
    "고객 신뢰를 얻는 방법은?"
]

for q in questions:
    print(f"\n질문: {q}")
    answer = glm.chat(q)
    print(f"답변: {answer}")
    glm.clear_history()  # 각 질문을 독립적으로
```

### 예제 4: 모든 기능 통합

```python
# 전체 예제 파일 실행
python glm_example.py
```

선택 메뉴가 나타나면 원하는 예제 번호를 입력하세요.

---

## 🔧 고급 설정

### 다양한 모델 사용

GLM은 여러 모델을 제공합니다:

```python
# 빠른 응답 (기본)
response = glm.chat("질문", model="glm-4-flash")

# 균형잡힌 성능
response = glm.chat("질문", model="glm-4")

# 경제적인 옵션
response = glm.chat("질문", model="glm-3-turbo")
```

### 히스토리 저장 여부 제어

```python
# 히스토리에 저장 (기본)
response = glm.chat("질문", save_history=True)

# 히스토리에 저장 안 함 (일회성 질문)
response = glm.chat("질문", save_history=False)
```

### 컨텍스트가 긴 대화

```python
glm = GLMInteraction()

# 첫 번째 질문
glm.chat("아마존 구매대행 사업에 대해 알려주세요.")

# 이어지는 질문 (이전 대화를 기억)
glm.chat("거기서 주의할 점은 뭔가요?")
glm.chat("구체적으로 어떻게 시작하나요?")

# 필요시 히스토리 확인
history = glm.get_history()
```

---

## ❗ 문제 해결

### API 키 오류

```
ValueError: GLM_API_KEY가 설정되지 않았습니다.
```

**해결방법:**
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. 파일에 `GLM_API_KEY=your_key` 형식으로 작성되었는지 확인
3. API 키가 유효한지 확인

### 패키지 설치 오류

```
ModuleNotFoundError: No module named 'zhipuai'
```

**해결방법:**
```bash
pip install zhipuai==2.0.1
```

### 네트워크 오류

```
GLM API 호출 중 오류 발생: Connection timeout
```

**해결방법:**
1. 인터넷 연결 확인
2. 방화벽 설정 확인
3. API 서버 상태 확인

### 응답이 느릴 때

**해결방법:**
1. 스트리밍 모드 사용:
   ```python
   response = glm.chat("질문", stream=True)
   ```
2. 더 빠른 모델 사용:
   ```python
   response = glm.chat("질문", model="glm-4-flash")
   ```

---

## 🎓 학습 자료

### 공식 문서
- [Zhipu AI 개발자 문서](https://open.bigmodel.cn/dev/api)
- [Python SDK 가이드](https://github.com/zhipuai/zhipuai-sdk-python)

### 모델 비교

| 모델 | 속도 | 품질 | 비용 | 추천 용도 |
|------|------|------|------|-----------|
| glm-4-flash | ⚡⚡⚡ | ⭐⭐ | 💰 | 빠른 응답, 간단한 작업 |
| glm-4 | ⚡⚡ | ⭐⭐⭐ | 💰💰 | 균형잡힌 작업 |
| glm-3-turbo | ⚡⚡⚡ | ⭐⭐ | 💰 | 대량 처리 |

---

## 💼 비즈니스 활용 팁

### 1. 상품 분석 자동화

매일 새로운 아마존 상품을 분석하여 수익성 높은 제품 발굴

### 2. 다국어 지원

영어 상품 정보를 자연스러운 한국어로 번역하여 고객 경험 향상

### 3. SEO 최적화

AI가 생성한 태그로 네이버 검색 노출 증대

### 4. 고객 응대

상품 문의에 대한 자동 응답 시스템 구축

### 5. 시장 조사

경쟁사 분석 및 트렌드 파악

---

## 📞 지원

문제가 발생하거나 질문이 있으면:
- GitHub Issues에 문의
- 프로젝트 문서 확인
- GLM 공식 지원 채널 이용

---

**마지막 업데이트:** 2025-12-01
**버전:** 1.0.0
