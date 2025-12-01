# GLM API 설정 가이드

## 개요
이 프로젝트에 智谱AI GLM API가 성공적으로 설정되었습니다.

## API 키
API 키: `0dded578165b4c92a340970e94f94c5d.dNlQK1FhpZEVrN7o`

이 API 키는 `.env` 파일에 `GLM_API_KEY` 환경 변수로 저장되어 있습니다.

## 설치된 패키지
- `zhipuai==2.1.5.20250825` - 智谱AI 공식 Python SDK

## 사용 방법

### 기본 사용 예제

```python
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# GLM 클라이언트 초기화
client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))

# 채팅 완료 요청
response = client.chat.completions.create(
    model="glm-4-plus",  # 또는 "glm-4", "glm-3-turbo"
    messages=[
        {
            "role": "user",
            "content": "안녕하세요! 아마존 스마트스토어 자동화에 대해 알려주세요."
        }
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

### 스트리밍 모드

```python
response = client.chat.completions.create(
    model="glm-4-plus",
    messages=[
        {"role": "user", "content": "긴 답변이 필요한 질문"}
    ],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## 사용 가능한 모델

- `glm-4-plus` - 최신 고성능 모델 (권장)
- `glm-4` - 표준 모델
- `glm-3-turbo` - 빠른 응답 모델

## 테스트 스크립트

프로젝트에 포함된 `glm_api_test.py` 스크립트로 GLM API를 테스트할 수 있습니다:

```bash
python glm_api_test.py
```

## 주의사항

### 네트워크 환경
현재 개발 환경에서는 네트워크 제한으로 인해 GLM API 서버(`open.bigmodel.cn`)에 직접 접근할 수 없습니다.

**로컬 환경에서 테스트 권장:**
- 네트워크 제한이 없는 환경에서 실행
- 프록시 설정이 필요한 경우 스크립트에서 프록시 환경 변수를 제거하지 않도록 수정

### 프록시 설정
`glm_api_test.py` 스크립트는 프록시 환경 변수를 자동으로 제거합니다. 프록시가 필요한 경우 다음 코드를 제거하세요:

```python
# 프록시 환경 변수 제거 (GLM API 접근을 위해)
for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]
```

## 비용 및 사용량

- API 호출 시 토큰 사용량이 과금됩니다
- `response.usage` 객체에서 토큰 사용량을 확인할 수 있습니다:
  - `prompt_tokens`: 입력 토큰 수
  - `completion_tokens`: 출력 토큰 수
  - `total_tokens`: 총 토큰 수

## 통합 예제: 아마존 상품 설명 생성

```python
from zhipuai import ZhipuAI
import os
from dotenv import load_dotenv

load_dotenv()

def generate_product_description(product_name, features):
    """GLM을 사용하여 아마존 상품 설명 생성"""

    client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))

    prompt = f"""
    다음 아마존 상품에 대한 매력적인 한국어 상품 설명을 작성해주세요:

    상품명: {product_name}
    주요 특징: {features}

    요구사항:
    - 고객의 구매 욕구를 자극하는 설명
    - 주요 특징과 이점을 명확히 설명
    - 2-3문단으로 구성
    """

    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=500
    )

    return response.choices[0].message.content

# 사용 예
description = generate_product_description(
    "무선 블루투스 이어폰",
    "노이즈 캔슬링, 30시간 배터리, IPX7 방수"
)
print(description)
```

## 문제 해결

### Connection Error
- 네트워크 연결 확인
- API 키 유효성 확인
- 프록시 설정 확인

### API Key Error
- `.env` 파일에 `GLM_API_KEY`가 올바르게 설정되었는지 확인
- API 키 형식이 올바른지 확인

## 추가 리소스

- [智谱AI 공식 문서](https://open.bigmodel.cn/dev/api)
- [GitHub Repository](https://github.com/zhipuai/zhipuai-sdk-python)
