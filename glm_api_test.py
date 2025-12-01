"""
GLM API 테스트 스크립트
智谱AI GLM 모델을 사용한 기본 테스트
"""

import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# .env 파일에서 환경변수 로드
load_dotenv()

# 프록시 환경 변수 제거 (GLM API 접근을 위해)
for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if proxy_var in os.environ:
        del os.environ[proxy_var]

def test_glm_api():
    """GLM API 연결 및 기본 테스트"""

    # API 키 가져오기
    api_key = os.getenv("GLM_API_KEY")

    if not api_key:
        print("❌ Error: GLM_API_KEY가 .env 파일에 설정되지 않았습니다.")
        return

    print(f"✓ API 키 로드 완료: {api_key[:20]}...")

    try:
        # ZhipuAI 클라이언트 초기화
        client = ZhipuAI(api_key=api_key)
        print("✓ GLM 클라이언트 초기화 완료")

        # 간단한 테스트 요청
        print("\n📝 GLM에 테스트 메시지 전송 중...")

        response = client.chat.completions.create(
            model="glm-4-plus",  # 또는 "glm-4", "glm-3-turbo" 등
            messages=[
                {
                    "role": "user",
                    "content": "안녕하세요! 당신은 누구인가요? 간단히 소개해주세요."
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        # 응답 출력
        print("\n✓ GLM 응답 수신 완료:")
        print("=" * 60)
        print(response.choices[0].message.content)
        print("=" * 60)

        # 모델 정보 출력
        print(f"\n📊 모델 정보:")
        print(f"  - 모델: {response.model}")
        print(f"  - 토큰 사용량: {response.usage.total_tokens} (입력: {response.usage.prompt_tokens}, 출력: {response.usage.completion_tokens})")

        print("\n✅ GLM API 테스트 성공!")

    except Exception as e:
        print(f"\n❌ GLM API 테스트 실패: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")
        import traceback
        print(f"\n상세 오류 정보:")
        traceback.print_exc()

def test_glm_streaming():
    """GLM API 스트리밍 테스트"""

    api_key = os.getenv("GLM_API_KEY")

    if not api_key:
        print("❌ Error: GLM_API_KEY가 .env 파일에 설정되지 않았습니다.")
        return

    try:
        client = ZhipuAI(api_key=api_key)

        print("\n📝 GLM 스트리밍 모드 테스트 중...")
        print("=" * 60)

        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {
                    "role": "user",
                    "content": "아마존 스마트스토어 자동화에 대해 3가지 핵심 기능을 알려주세요."
                }
            ],
            stream=True
        )

        # 스트리밍 응답 출력
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

        print("\n" + "=" * 60)
        print("✅ 스트리밍 테스트 성공!")

    except Exception as e:
        print(f"\n❌ 스트리밍 테스트 실패: {str(e)}")
        import traceback
        print(f"\n상세 오류 정보:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 GLM API 테스트 시작\n")

    # 기본 테스트
    test_glm_api()

    # 스트리밍 테스트
    print("\n" + "=" * 60 + "\n")
    test_glm_streaming()

    print("\n🎉 모든 테스트 완료!")
