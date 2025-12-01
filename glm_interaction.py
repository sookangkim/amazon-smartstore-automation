"""
GLM AI 상호작용 모듈
GLM API를 사용하여 AI와 대화하고 상품 분석, 번역 등의 작업을 수행합니다.
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 환경 변수 로드
load_dotenv()


class GLMInteraction:
    """GLM AI와 상호작용하는 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        GLM 클라이언트 초기화

        Args:
            api_key: GLM API 키 (없으면 환경변수에서 로드)
        """
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        if not self.api_key:
            raise ValueError("GLM_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        self.client = ZhipuAI(api_key=self.api_key)
        self.conversation_history: List[Dict[str, str]] = []

    def chat(self, message: str, model: str = "glm-4-flash",
             stream: bool = False, save_history: bool = True) -> str:
        """
        GLM과 대화하기

        Args:
            message: 사용자 메시지
            model: 사용할 GLM 모델 (glm-4-flash, glm-4, glm-3-turbo 등)
            stream: 스트리밍 모드 사용 여부
            save_history: 대화 히스토리 저장 여부

        Returns:
            GLM의 응답 메시지
        """
        # 대화 히스토리에 사용자 메시지 추가
        if save_history:
            self.conversation_history.append({
                "role": "user",
                "content": message
            })

        try:
            if stream:
                # 스트리밍 모드
                response = self.client.chat.completions.create(
                    model=model,
                    messages=self.conversation_history if save_history else [{"role": "user", "content": message}],
                    stream=True
                )

                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        full_response += content
                print()  # 줄바꿈

                if save_history:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": full_response
                    })

                return full_response
            else:
                # 일반 모드
                response = self.client.chat.completions.create(
                    model=model,
                    messages=self.conversation_history if save_history else [{"role": "user", "content": message}]
                )

                assistant_message = response.choices[0].message.content

                if save_history:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message
                    })

                return assistant_message

        except Exception as e:
            error_msg = f"GLM API 호출 중 오류 발생: {str(e)}"
            print(error_msg)
            return error_msg

    def analyze_product(self, product_info: Dict) -> str:
        """
        상품 정보를 분석하여 판매 가능성 평가

        Args:
            product_info: 상품 정보 딕셔너리

        Returns:
            분석 결과
        """
        prompt = f"""
다음 아마존 상품 정보를 분석하고 한국 네이버 스마트스토어에서의 판매 가능성을 평가해주세요:

상품명: {product_info.get('title', 'N/A')}
가격: ${product_info.get('price', 'N/A')}
카테고리: {product_info.get('category', 'N/A')}
평점: {product_info.get('rating', 'N/A')}
리뷰 수: {product_info.get('review_count', 'N/A')}

다음 항목을 분석해주세요:
1. 한국 시장 적합성 (1-10점)
2. 예상 마진율
3. 경쟁 강도
4. 추천 판매가격 (원화)
5. 마케팅 포인트
"""
        return self.chat(prompt, save_history=False)

    def translate_product(self, product_info: Dict) -> Dict[str, str]:
        """
        상품 정보를 한국어로 번역

        Args:
            product_info: 상품 정보 딕셔너리

        Returns:
            번역된 정보 딕셔너리
        """
        prompt = f"""
다음 아마존 상품 정보를 한국어로 자연스럽게 번역해주세요.
SEO에 최적화되고 고객 구매욕구를 자극할 수 있도록 작성해주세요.

상품명: {product_info.get('title', '')}
상세설명: {product_info.get('description', '')}

JSON 형식으로 응답해주세요:
{{
    "title": "번역된 상품명",
    "description": "번역된 상세설명"
}}
"""
        response = self.chat(prompt, save_history=False)

        # JSON 파싱 시도
        try:
            import json
            # JSON 부분만 추출
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass

        return {"title": "", "description": response}

    def generate_product_tags(self, product_title: str) -> List[str]:
        """
        상품에 적합한 태그 생성

        Args:
            product_title: 상품명

        Returns:
            태그 리스트
        """
        prompt = f"""
다음 상품에 적합한 한국어 검색 태그를 10개 생성해주세요.
상품명: {product_title}

쉼표로 구분된 태그 목록만 응답해주세요.
"""
        response = self.chat(prompt, save_history=False)
        tags = [tag.strip() for tag in response.split(',')]
        return tags[:10]

    def clear_history(self):
        """대화 히스토리 초기화"""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """대화 히스토리 가져오기"""
        return self.conversation_history


def main():
    """메인 함수 - 대화형 인터페이스"""
    print("=" * 60)
    print("GLM AI 대화 시스템")
    print("=" * 60)
    print("명령어:")
    print("  - 'exit' 또는 'quit': 종료")
    print("  - 'clear': 대화 히스토리 초기화")
    print("  - 'history': 대화 히스토리 보기")
    print("  - 'stream on/off': 스트리밍 모드 전환")
    print("=" * 60)

    try:
        # GLM 클라이언트 초기화
        glm = GLMInteraction()
        stream_mode = False

        print("\nGLM과 대화를 시작합니다. 무엇이든 물어보세요!\n")

        while True:
            try:
                user_input = input("\n당신: ").strip()

                if not user_input:
                    continue

                # 명령어 처리
                if user_input.lower() in ['exit', 'quit']:
                    print("\n대화를 종료합니다. 안녕히 가세요!")
                    break

                elif user_input.lower() == 'clear':
                    glm.clear_history()
                    print("\n대화 히스토리가 초기화되었습니다.")
                    continue

                elif user_input.lower() == 'history':
                    print("\n=== 대화 히스토리 ===")
                    for i, msg in enumerate(glm.get_history(), 1):
                        role = "당신" if msg['role'] == 'user' else "GLM"
                        print(f"\n[{i}] {role}: {msg['content'][:100]}...")
                    continue

                elif user_input.lower().startswith('stream '):
                    mode = user_input.split()[1].lower()
                    if mode == 'on':
                        stream_mode = True
                        print("\n스트리밍 모드가 활성화되었습니다.")
                    elif mode == 'off':
                        stream_mode = False
                        print("\n스트리밍 모드가 비활성화되었습니다.")
                    continue

                # GLM과 대화
                print("\nGLM: ", end="" if stream_mode else "")
                response = glm.chat(user_input, stream=stream_mode)

                if not stream_mode:
                    print(response)

            except KeyboardInterrupt:
                print("\n\n대화를 종료합니다.")
                break
            except Exception as e:
                print(f"\n오류 발생: {str(e)}")
                continue

    except ValueError as e:
        print(f"\n초기화 오류: {str(e)}")
        print("\n.env 파일에 GLM_API_KEY를 설정해주세요.")
        print("예시: GLM_API_KEY=your_api_key_here")
    except Exception as e:
        print(f"\n예기치 않은 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
