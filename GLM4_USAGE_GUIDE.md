# GLM-4 사용 가이드

## 목차
1. [설치 및 설정](#설치-및-설정)
2. [기본 사용법](#기본-사용법)
3. [주요 기능](#주요-기능)
4. [실전 예제](#실전-예제)
5. [문제 해결](#문제-해결)

---

## 설치 및 설정

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 발급

1. [ZhipuAI 웹사이트](https://open.bigmodel.cn/)에 접속
2. 회원가입 및 로그인
3. API 키 발급 받기

### 3. 환경 변수 설정

`.env` 파일 생성 (`.env.template` 참고):

```bash
cp .env.template .env
```

`.env` 파일에 API 키 설정:

```
ZHIPU_API_KEY=your_actual_api_key_here
```

---

## 기본 사용법

### GLM4Service 초기화

```python
from glm4_integration import GLM4Service

# 초기화 (환경 변수에서 API 키 자동 로드)
glm = GLM4Service()

# 또는 직접 API 키 전달
glm = GLM4Service(api_key="your_api_key")
```

### 기본 대화

```python
# 간단한 질문-답변
response = glm.chat([
    {"role": "user", "content": "네이버 스마트스토어 운영 팁을 알려주세요"}
])
print(response)
```

---

## 주요 기능

### 1. 상품 설명 자동 생성

```python
description = glm.generate_product_description(
    product_name="프리미엄 무선 이어폰",
    features=[
        "노이즈 캔슬링 기능",
        "30시간 재생 시간",
        "IPX7 방수",
        "블루투스 5.3"
    ],
    keywords=["무선이어폰", "노캔", "프리미엄"]
)
print(description)
```

**출력 예시:**
```
🎧 프리미엄 무선 이어폰 - 완벽한 음악 경험을 선사합니다

최고급 노이즈 캔슬링 기술로 주변 소음을 차단하고,
순수한 음악에만 집중할 수 있습니다...
```

### 2. 상품 제목 최적화

```python
optimized_title = glm.optimize_product_title(
    original_title="Wireless Earbuds with ANC and Long Battery Life",
    max_length=50
)
print(optimized_title)
```

**출력 예시:**
```
프리미엄 무선이어폰 노이즈캔슬링 30시간 재생 방수
```

### 3. 텍스트 번역 및 개선

```python
translated = glm.translate_and_improve(
    text="Premium quality wireless earbuds with active noise cancellation",
    source_lang="영어",
    target_lang="한국어"
)
print(translated)
```

**출력 예시:**
```
액티브 노이즈 캔슬링 기능을 갖춘 프리미엄 무선 이어폰
```

### 4. 고객 문의 자동 응답

```python
answer = glm.answer_customer_inquiry(
    inquiry="배송은 언제쯤 도착하나요?",
    product_info="상품명: 프리미엄 무선 이어폰\n재고: 있음"
)
print(answer)
```

**출력 예시:**
```
안녕하세요, 고객님.
주문하신 상품은 결제 완료 후 1-2일 이내에 발송되며,
발송 후 1-2일 내로 도착 예정입니다.
감사합니다.
```

### 5. 키워드 생성

```python
keywords = glm.generate_keywords(
    product_name="프리미엄 무선 이어폰",
    category="이어폰/헤드폰",
    count=10
)
print(keywords)
```

**출력 예시:**
```
['무선이어폰', '블루투스이어폰', '노이즈캔슬링', '프리미엄이어폰',
 '무선헤드셋', 'ANC이어폰', '방수이어폰', '장시간재생', ...]
```

---

## 실전 예제

### 예제 1: 아마존 상품을 네이버 스마트스토어용으로 변환

```python
from glm4_integration import GLM4Service

glm = GLM4Service()

# 아마존 상품 정보
amazon_title = "Sony WH-1000XM5 Wireless Noise Canceling Headphones"
amazon_description = "Industry-leading noise cancellation with 8 microphones"

# 1. 제목 최적화
korean_title = glm.optimize_product_title(amazon_title, max_length=50)
print(f"최적화된 제목: {korean_title}")

# 2. 설명 번역 및 개선
korean_description = glm.translate_and_improve(amazon_description)
print(f"번역된 설명: {korean_description}")

# 3. 상세 설명 생성
detailed_description = glm.generate_product_description(
    product_name=korean_title,
    features=[
        "업계 최고의 노이즈 캔슬링",
        "8개 마이크 시스템",
        "30시간 배터리",
        "프리미엄 사운드"
    ],
    keywords=["소니", "헤드폰", "노이즈캔슬링"]
)
print(f"상세 설명:\n{detailed_description}")

# 4. SEO 키워드 생성
seo_keywords = glm.generate_keywords(
    product_name=korean_title,
    category="헤드폰",
    count=15
)
print(f"SEO 키워드: {', '.join(seo_keywords)}")
```

### 예제 2: 대량 상품 처리

```python
import pandas as pd
from glm4_integration import GLM4Service

glm = GLM4Service()

# 상품 데이터 로드
products = pd.read_excel('amazon_products.xlsx')

# 각 상품 처리
for idx, product in products.iterrows():
    # 제목 최적화
    optimized_title = glm.optimize_product_title(
        product['title'],
        max_length=50
    )

    # 설명 생성
    description = glm.generate_product_description(
        product_name=optimized_title,
        features=product['features'].split(','),
        keywords=product['keywords'].split(',')
    )

    # 결과 저장
    products.at[idx, 'korean_title'] = optimized_title
    products.at[idx, 'korean_description'] = description

    print(f"처리 완료: {idx + 1}/{len(products)}")

# 결과 저장
products.to_excel('processed_products.xlsx', index=False)
print("모든 상품 처리 완료!")
```

### 예제 3: 고객 문의 자동 응답 시스템

```python
from glm4_integration import GLM4Service
import json

glm = GLM4Service()

# 고객 문의 데이터
inquiries = [
    "배송 기간이 얼마나 걸리나요?",
    "환불이 가능한가요?",
    "제품 색상이 다른 것도 있나요?",
]

product_info = """
상품명: 프리미엄 무선 이어폰
가격: 89,000원
색상: 블랙, 화이트
배송: 무료배송 (1-2일)
반품: 7일 이내 가능
"""

# 각 문의에 대한 응답 생성
for inquiry in inquiries:
    answer = glm.answer_customer_inquiry(
        inquiry=inquiry,
        product_info=product_info
    )
    print(f"Q: {inquiry}")
    print(f"A: {answer}\n")
    print("-" * 50)
```

---

## 고급 사용법

### 사용자 정의 프롬프트

```python
# 직접 chat 메서드 사용
messages = [
    {"role": "user", "content": "네이버 쇼핑 검색 1위를 위한 상품명을 만들어주세요"}
]

response = glm.chat(
    messages=messages,
    temperature=0.8,  # 창의성 높게
    max_tokens=1000
)
print(response)
```

### 다중 턴 대화

```python
# 대화 이력 유지
conversation_history = []

# 첫 번째 메시지
conversation_history.append({
    "role": "user",
    "content": "무선 이어폰 상품 설명을 작성해주세요"
})

response1 = glm.chat(conversation_history)
conversation_history.append({
    "role": "assistant",
    "content": response1
})

# 두 번째 메시지 (이전 대화 맥락 유지)
conversation_history.append({
    "role": "user",
    "content": "좀 더 전문적인 톤으로 수정해주세요"
})

response2 = glm.chat(conversation_history)
print(response2)
```

---

## 문제 해결

### API 키 오류

**오류 메시지:**
```
ValueError: ZHIPU_API_KEY가 설정되지 않았습니다.
```

**해결 방법:**
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. `.env` 파일에 `ZHIPU_API_KEY=your_key` 가 올바르게 설정되었는지 확인
3. API 키가 유효한지 ZhipuAI 웹사이트에서 확인

### 연결 오류

**오류 메시지:**
```
ConnectionError: API 서버에 연결할 수 없습니다
```

**해결 방법:**
1. 인터넷 연결 확인
2. 방화벽 설정 확인
3. VPN 사용 시 중국 서버 접근 가능 여부 확인

### 할당량 초과

**오류 메시지:**
```
QuotaExceeded: API 호출 한도를 초과했습니다
```

**해결 방법:**
1. ZhipuAI 대시보드에서 사용량 확인
2. 요금제 업그레이드 또는 다음 주기까지 대기
3. 캐싱을 사용하여 중복 요청 줄이기

### 느린 응답 속도

**해결 방법:**
1. `max_tokens` 값을 줄여서 응답 길이 제한
2. 여러 요청을 배치로 처리하지 말고 순차 처리
3. 간단한 작업은 `temperature` 값을 낮춰서 처리

---

## 테스트 실행

```bash
# 통합 테스트 실행
python glm4_integration.py
```

성공적으로 실행되면 다음과 같은 출력을 볼 수 있습니다:

```
==================================================
GLM-4 통합 테스트
==================================================

1. 기본 대화 테스트:
응답: 안녕하세요! 아마존 스마트스토어 자동화를 도와드리겠습니다...

2. 상품 설명 생성:
생성된 설명:
...

==================================================
모든 테스트가 완료되었습니다!
==================================================
```

---

## 참고 자료

- [ZhipuAI 공식 문서](https://open.bigmodel.cn/dev/api)
- [GLM-4 모델 가이드](https://open.bigmodel.cn/docs/glm-4)
- [Python SDK GitHub](https://github.com/zhipuai/zhipuai-sdk-python)

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 문의

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.
