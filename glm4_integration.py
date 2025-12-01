"""
GLM-4 통합 모듈
아마존 스마트스토어 자동화를 위한 GLM-4 AI 모델 통합

주요 기능:
- 상품 설명 자동 생성
- 텍스트 번역 및 개선
- 상품 제목 최적화
- 고객 문의 자동 응답
"""

import os
from typing import List, Dict, Optional
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()


class GLM4Service:
    """GLM-4 AI 모델 서비스 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        GLM-4 서비스 초기화

        Args:
            api_key: ZhipuAI API 키 (없으면 환경 변수에서 로드)
        """
        self.api_key = api_key or os.getenv('ZHIPU_API_KEY')
        if not self.api_key:
            raise ValueError("ZHIPU_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

        self.client = ZhipuAI(api_key=self.api_key)
        logger.info("GLM-4 서비스가 초기화되었습니다.")

    def chat(self,
             messages: List[Dict[str, str]],
             model: str = "glm-4",
             temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        """
        GLM-4와 대화

        Args:
            messages: 대화 메시지 리스트 [{"role": "user", "content": "..."}]
            model: 사용할 모델 (기본값: glm-4)
            temperature: 창의성 수준 (0.0~1.0)
            max_tokens: 최대 토큰 수

        Returns:
            AI 응답 텍스트
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GLM-4 API 호출 실패: {e}")
            raise

    def generate_product_description(self,
                                     product_name: str,
                                     features: List[str],
                                     keywords: Optional[List[str]] = None) -> str:
        """
        상품 설명 자동 생성

        Args:
            product_name: 상품명
            features: 상품 특징 리스트
            keywords: 포함할 키워드 (선택사항)

        Returns:
            생성된 상품 설명
        """
        features_text = "\n".join([f"- {f}" for f in features])
        keywords_text = ", ".join(keywords) if keywords else ""

        prompt = f"""다음 정보를 바탕으로 네이버 스마트스토어용 매력적인 상품 설명을 작성해주세요.

상품명: {product_name}

주요 특징:
{features_text}

{f'포함할 키워드: {keywords_text}' if keywords_text else ''}

요구사항:
1. 고객의 구매욕을 자극하는 내용
2. SEO 최적화를 고려한 키워드 배치
3. 읽기 쉬운 구조 (제목, 본문, 특징)
4. 300-500자 분량
"""

        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.8)

    def optimize_product_title(self,
                              original_title: str,
                              max_length: int = 50) -> str:
        """
        상품 제목 최적화

        Args:
            original_title: 원본 제목
            max_length: 최대 길이

        Returns:
            최적화된 제목
        """
        prompt = f"""다음 상품 제목을 네이버 스마트스토어에 최적화된 제목으로 개선해주세요.

원본 제목: {original_title}

요구사항:
1. 최대 {max_length}자 이내
2. 검색 최적화를 고려한 키워드 배치
3. 고객의 관심을 끄는 표현
4. 불필요한 특수문자 제거

개선된 제목만 출력해주세요."""

        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.7)

    def translate_and_improve(self,
                             text: str,
                             source_lang: str = "영어",
                             target_lang: str = "한국어") -> str:
        """
        텍스트 번역 및 개선

        Args:
            text: 번역할 텍스트
            source_lang: 원본 언어
            target_lang: 대상 언어

        Returns:
            번역 및 개선된 텍스트
        """
        prompt = f"""다음 {source_lang} 텍스트를 {target_lang}로 번역하고, 자연스럽게 개선해주세요.

원본 텍스트:
{text}

요구사항:
1. 자연스러운 {target_lang} 표현
2. 상품 설명에 적합한 문체
3. 의미 전달을 정확하게"""

        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.5)

    def answer_customer_inquiry(self,
                               inquiry: str,
                               product_info: Optional[str] = None) -> str:
        """
        고객 문의 자동 응답

        Args:
            inquiry: 고객 문의 내용
            product_info: 관련 상품 정보 (선택사항)

        Returns:
            자동 생성된 답변
        """
        context = f"\n\n관련 상품 정보:\n{product_info}" if product_info else ""

        prompt = f"""다음 고객 문의에 대해 친절하고 전문적인 답변을 작성해주세요.

고객 문의:
{inquiry}{context}

요구사항:
1. 친절하고 정중한 말투
2. 명확하고 구체적인 답변
3. 고객 만족을 위한 배려
4. 200자 이내의 간결한 답변"""

        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature=0.6)

    def generate_keywords(self,
                         product_name: str,
                         category: str,
                         count: int = 10) -> List[str]:
        """
        상품 키워드 생성

        Args:
            product_name: 상품명
            category: 상품 카테고리
            count: 생성할 키워드 개수

        Returns:
            키워드 리스트
        """
        prompt = f"""다음 상품에 대한 검색 최적화 키워드 {count}개를 생성해주세요.

상품명: {product_name}
카테고리: {category}

요구사항:
1. 네이버 쇼핑 검색에 효과적인 키워드
2. 관련성 높은 키워드
3. 각 키워드를 줄바꿈으로 구분
4. 키워드만 출력 (번호나 기호 없이)"""

        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, temperature=0.7)

        # 응답을 키워드 리스트로 변환
        keywords = [k.strip() for k in response.split('\n') if k.strip()]
        return keywords[:count]


def main():
    """사용 예시"""
    try:
        # GLM-4 서비스 초기화
        glm = GLM4Service()

        print("=" * 50)
        print("GLM-4 통합 테스트")
        print("=" * 50)

        # 1. 간단한 대화 테스트
        print("\n1. 기본 대화 테스트:")
        response = glm.chat([
            {"role": "user", "content": "안녕하세요! 아마존 스마트스토어 자동화를 도와주세요."}
        ])
        print(f"응답: {response}")

        # 2. 상품 설명 생성
        print("\n2. 상품 설명 생성:")
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
        print(f"생성된 설명:\n{description}")

        # 3. 제목 최적화
        print("\n3. 제목 최적화:")
        optimized_title = glm.optimize_product_title(
            "Wireless Earbuds with ANC and Long Battery Life"
        )
        print(f"최적화된 제목: {optimized_title}")

        # 4. 번역 및 개선
        print("\n4. 텍스트 번역:")
        translated = glm.translate_and_improve(
            "Premium quality wireless earbuds with active noise cancellation"
        )
        print(f"번역 결과: {translated}")

        # 5. 키워드 생성
        print("\n5. 키워드 생성:")
        keywords = glm.generate_keywords(
            product_name="프리미엄 무선 이어폰",
            category="이어폰/헤드폰",
            count=5
        )
        print(f"생성된 키워드: {', '.join(keywords)}")

        print("\n" + "=" * 50)
        print("모든 테스트가 완료되었습니다!")
        print("=" * 50)

    except Exception as e:
        logger.error(f"오류 발생: {e}")
        print(f"\n오류: {e}")
        print("\n.env 파일에 ZHIPU_API_KEY가 설정되어 있는지 확인하세요.")


if __name__ == "__main__":
    main()
