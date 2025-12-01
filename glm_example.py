"""
GLM AI 상호작용 예제
다양한 GLM 활용 사례를 보여줍니다.
"""

from glm_interaction import GLMInteraction


def example_simple_chat():
    """기본 대화 예제"""
    print("\n" + "=" * 60)
    print("예제 1: 간단한 대화")
    print("=" * 60)

    glm = GLMInteraction()

    # 간단한 질문
    response = glm.chat("안녕하세요! 당신은 누구인가요?")
    print(f"\nGLM: {response}")

    # 연속 대화 (히스토리 유지)
    response = glm.chat("오늘 날씨가 좋네요. 무엇을 하면 좋을까요?")
    print(f"\nGLM: {response}")


def example_product_analysis():
    """상품 분석 예제"""
    print("\n" + "=" * 60)
    print("예제 2: 아마존 상품 분석")
    print("=" * 60)

    glm = GLMInteraction()

    # 샘플 상품 정보
    product = {
        "title": "CeraVe Moisturizing Cream | Body and Face Moisturizer for Dry Skin",
        "price": 19.99,
        "category": "Beauty & Personal Care",
        "rating": 4.7,
        "review_count": 98543
    }

    print(f"\n분석할 상품: {product['title']}")
    print(f"가격: ${product['price']}")

    # 상품 분석
    analysis = glm.analyze_product(product)
    print(f"\n분석 결과:\n{analysis}")


def example_translation():
    """번역 예제"""
    print("\n" + "=" * 60)
    print("예제 3: 상품 정보 번역")
    print("=" * 60)

    glm = GLMInteraction()

    # 샘플 상품 정보
    product = {
        "title": "Apple AirPods Pro (2nd Generation) with MagSafe Case",
        "description": "Active Noise Cancellation with Transparency mode. Personalized Spatial Audio with dynamic head tracking. Adaptive EQ."
    }

    print(f"\n원문 제목: {product['title']}")
    print(f"원문 설명: {product['description']}")

    # 번역
    translated = glm.translate_product(product)
    print(f"\n번역 결과:")
    print(f"제목: {translated.get('title', 'N/A')}")
    print(f"설명: {translated.get('description', 'N/A')}")


def example_tag_generation():
    """태그 생성 예제"""
    print("\n" + "=" * 60)
    print("예제 4: 검색 태그 생성")
    print("=" * 60)

    glm = GLMInteraction()

    product_title = "무선 블루투스 이어폰 노이즈 캔슬링 기능"

    print(f"\n상품명: {product_title}")

    # 태그 생성
    tags = glm.generate_product_tags(product_title)
    print(f"\n생성된 태그:")
    for i, tag in enumerate(tags, 1):
        print(f"  {i}. {tag}")


def example_streaming():
    """스트리밍 모드 예제"""
    print("\n" + "=" * 60)
    print("예제 5: 스트리밍 모드 대화")
    print("=" * 60)

    glm = GLMInteraction()

    print("\n질문: 아마존에서 한국으로 상품을 수입할 때 주의사항은?")
    print("\nGLM (스트리밍): ", end="")

    # 스트리밍 모드로 응답 받기
    response = glm.chat(
        "아마존에서 한국으로 상품을 수입할 때 주의사항 5가지를 알려주세요.",
        stream=True
    )


def example_business_consultation():
    """비즈니스 컨설팅 예제"""
    print("\n" + "=" * 60)
    print("예제 6: 비즈니스 전략 컨설팅")
    print("=" * 60)

    glm = GLMInteraction()

    questions = [
        "아마존 구매대행 사업의 핵심 성공 요인은 무엇인가요?",
        "30-40% 마진을 유지하면서 경쟁력을 갖추려면 어떻게 해야 하나요?",
        "네이버 스마트스토어에서 매출을 높이는 방법을 3가지만 알려주세요."
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n질문 {i}: {question}")
        response = glm.chat(question)
        print(f"\nGLM: {response}")
        print("\n" + "-" * 60)

        # 히스토리 초기화 (각 질문을 독립적으로)
        if i < len(questions):
            glm.clear_history()


def main():
    """모든 예제 실행"""
    print("\n" + "=" * 60)
    print("GLM AI 활용 예제 모음")
    print("=" * 60)

    examples = [
        ("1", "간단한 대화", example_simple_chat),
        ("2", "상품 분석", example_product_analysis),
        ("3", "번역", example_translation),
        ("4", "태그 생성", example_tag_generation),
        ("5", "스트리밍", example_streaming),
        ("6", "비즈니스 컨설팅", example_business_consultation),
        ("0", "전체 실행", None)
    ]

    print("\n실행할 예제를 선택하세요:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")

    try:
        choice = input("\n선택 (번호 입력): ").strip()

        if choice == "0":
            # 모든 예제 실행
            for num, name, func in examples:
                if func:
                    try:
                        func()
                        input("\n계속하려면 Enter를 누르세요...")
                    except Exception as e:
                        print(f"\n오류 발생: {str(e)}")
                        continue
        else:
            # 선택한 예제만 실행
            for num, name, func in examples:
                if num == choice and func:
                    func()
                    break
            else:
                print("\n잘못된 선택입니다.")

    except ValueError as e:
        print(f"\n초기화 오류: {str(e)}")
        print("\n.env 파일에 GLM_API_KEY를 설정해주세요.")
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
