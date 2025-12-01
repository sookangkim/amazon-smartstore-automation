#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 스마트스토어 상품 등록 자동화 모듈
최향기 시스템 기반 구매대행 자동화 프로그램

작성일: 2025년 7월 31일
버전: v1.0
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode
import os
from pathlib import Path

# 안전한 설정 로더 임포트
try:
    from config_loader import SecureConfigLoader
except ImportError:
    SecureConfigLoader = None
    print("⚠️  config_loader 모듈을 찾을 수 없습니다. 환경 변수를 직접 사용합니다.")

# 로깅 설정
logger = logging.getLogger(__name__)

@dataclass
class NaverProductData:
    """네이버 스마트스토어 상품 등록 데이터"""
    product_name: str
    category_id: str
    price: int
    discount_price: int
    description: str
    brand_name: str
    origin_country: str
    manufacturer: str
    images: List[str]
    delivery_fee: int
    delivery_method: str
    status: str = "SALE"  # SALE, SOLD_OUT, STOP
    adult_product: bool = False
    
class NaverSmartStoreAPI:
    """네이버 스마트스토어 커머스 API 클래스"""
    
    def __init__(self, client_id: str, client_secret: str, customer_id: str):
        """API 클라이언트 초기화"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.customer_id = customer_id
        self.base_url = "https://api.commerce.naver.com"
        self.session = None
        self.access_token = None
        
        # 카테고리 매핑 (아마존 -> 네이버)
        self.category_mapping = {
            "diet supplements": "50002617",      # 건강식품/다이어트
            "protein powder": "50002617",        # 건강식품/다이어트
            "granola cereal": "50000163",        # 식품/간편식
            "health supplements": "50002617",     # 건강식품/다이어트
            "baby clothes ballet": "50000671",   # 유아동패션/잡화
            "gaming accessories": "50000056",    # 컴퓨터/게임
            "medical equipment": "50002617",     # 건강식품/다이어트
            "brand accessories": "50000057",     # 패션잡화
            "home garden": "50000078",          # 생활/건강
            "sports outdoor": "50000080"        # 스포츠/레저
        }
    
    async def init_session(self):
        """HTTP 세션 초기화"""
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
    
    def _generate_signature(self, timestamp: str, method: str, uri: str, body: str = "") -> str:
        """API 서명 생성"""
        message = f"{timestamp}.{method}.{uri}"
        if body:
            message += f".{body}"
        
        signature = base64.b64encode(
            hmac.new(
                self.client_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return signature
    
    def _get_headers(self, method: str, uri: str, body: str = "") -> Dict[str, str]:
        """API 요청 헤더 생성"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, uri, body)
        
        headers = {
            'Content-Type': 'application/json',
            'X-Timestamp': timestamp,
            'X-API-KEY': self.client_id,
            'X-Customer': self.customer_id,
            'X-Signature': signature
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    async def authenticate(self) -> bool:
        """OAuth 2.0 인증"""
        try:
            auth_url = f"{self.base_url}/external/v1/oauth2/token"
            
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            async with self.session.post(auth_url, data=auth_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get('access_token')
                    logger.info("네이버 API 인증 성공")
                    return True
                else:
                    logger.error(f"네이버 API 인증 실패: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"네이버 API 인증 오류: {str(e)}")
            return False
    
    async def upload_image(self, image_url: str) -> Optional[str]:
        """이미지 업로드"""
        try:
            # 이미지 다운로드
            async with self.session.get(image_url) as response:
                if response.status != 200:
                    return None
                
                image_data = await response.read()
            
            # 네이버 이미지 업로드 API
            upload_url = f"{self.base_url}/external/v1/product-images/upload"
            
            # 멀티파트 폼 데이터 생성
            data = aiohttp.FormData()
            data.add_field('image', image_data, filename='product.jpg', content_type='image/jpeg')
            
            headers = self._get_headers('POST', '/external/v1/product-images/upload')
            del headers['Content-Type']  # 멀티파트에서는 자동 설정
            
            async with self.session.post(upload_url, data=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('imageUrl')
                else:
                    logger.error(f"이미지 업로드 실패: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"이미지 업로드 오류: {str(e)}")
            return None
    
    async def translate_description(self, description: str) -> str:
        """상품 설명 번역 (Papago API 활용)"""
        try:
            translate_url = "https://openapi.naver.com/v1/papago/n2mt"
            
            headers = {
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'source': 'en',
                'target': 'ko',
                'text': description[:5000]  # 5000자 제한
            }
            
            async with self.session.post(translate_url, data=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['message']['result']['translatedText']
                else:
                    logger.warning(f"번역 실패, 원문 사용: {response.status}")
                    return description
                    
        except Exception as e:
            logger.error(f"번역 오류: {str(e)}")
            return description
    
    def convert_amazon_to_naver_product(self, amazon_product: Dict) -> NaverProductData:
        """아마존 상품 데이터를 네이버 형식으로 변환"""
        try:
            # 가격 계산 (USD -> KRW, 마진 적용)
            usd_to_krw = 1350
            original_price_krw = int(amazon_product['price_usd'] * usd_to_krw)
            
            # 35% 마진 적용 (최향기 기준)
            selling_price = int(original_price_krw * 1.35)
            discount_price = int(selling_price * 0.95)  # 5% 할인가
            
            # 카테고리 매핑
            category_id = self.category_mapping.get(
                amazon_product.get('category', ''), 
                "50002617"  # 기본: 건강식품
            )
            
            # 상품명 생성 (브랜드 + 원제목)
            product_name = f"[{amazon_product.get('brand', 'Amazon')}] {amazon_product['title'][:80]}"
            
            # 상품 설명 생성
            description = f"""
🌟 아마존 베스트셀러 상품! 🌟

✅ 상품명: {amazon_product['title']}
✅ 브랜드: {amazon_product.get('brand', 'N/A')}
✅ 평점: {amazon_product.get('rating', 0)}점 ({amazon_product.get('review_count', 0)}개 리뷰)
✅ 아마존 베스트셀러 순위: {amazon_product.get('bsr_rank', 'N/A')}위

📦 배송 정보:
- 해외직구 상품 (미국 → 한국)
- 배송기간: 7-14일
- 관세 포함 가격

⚠️ 주의사항:
- 해외 제조사 직수입 상품
- 개봉 후 교환/환불 불가
- 제품 사용 전 성분 확인 필수

{amazon_product.get('description', '')}
            """.strip()
            
            return NaverProductData(
                product_name=product_name,
                category_id=category_id,
                price=selling_price,
                discount_price=discount_price,
                description=description,
                brand_name=amazon_product.get('brand', 'Amazon'),
                origin_country="미국",
                manufacturer=amazon_product.get('brand', 'Amazon'),
                images=[amazon_product.get('image_url', '')],
                delivery_fee=3000,  # 기본 배송비 3000원
                delivery_method="DELIVERY",
                status="SALE"
            )
            
        except Exception as e:
            logger.error(f"상품 데이터 변환 오류: {str(e)}")
            raise
    
    async def register_product(self, naver_product: NaverProductData) -> Optional[str]:
        """네이버 스마트스토어에 상품 등록"""
        try:
            # 이미지 업로드
            uploaded_images = []
            for image_url in naver_product.images:
                if image_url:
                    uploaded_url = await self.upload_image(image_url)
                    if uploaded_url:
                        uploaded_images.append(uploaded_url)
            
            # 상품 등록 데이터
            product_data = {
                "originProduct": {
                    "statusType": naver_product.status,
                    "saleType": "NEW",
                    "leafCategoryId": naver_product.category_id,
                    "name": naver_product.product_name,
                    "images": [{"url": url} for url in uploaded_images],
                    "detailContent": naver_product.description,
                    "brandName": naver_product.brand_name,
                    "manufacturerName": naver_product.manufacturer,
                    "originAreaInfo": {
                        "originAreaCode": "04",  # 미국
                        "content": naver_product.origin_country
                    },
                    "adultProduct": naver_product.adult_product
                },
                "smartstoreChannelProduct": {
                    "naverShoppingRegistration": True,
                    "channelProductName": naver_product.product_name,
                    "channelProductDisplayStatusType": "ON",
                    "salePrice": naver_product.price,
                    "discountPrice": naver_product.discount_price,
                    "deliveryInfo": {
                        "deliveryType": "DELIVERY",
                        "deliveryAttributeType": "NORMAL",
                        "deliveryCompany": "CJGLS",
                        "deliveryBundleGroupUsable": True,
                        "deliveryFee": {
                            "deliveryFeeType": "PAID",
                            "baseFee": naver_product.delivery_fee,
                            "freeConditionalAmount": 50000,
                            "deliveryFeeByArea": "NOT_DIFFERENTIAL",
                            "surchargesByArea": []
                        },
                        "returnDeliveryCompanyPriorityType": "PRIMARY",
                        "returnCenterCode": "10001",
                        "returnChargeName": "판매자",
                        "returnChargePhoneNumber": "1588-1234"
                    }
                }
            }
            
            # API 요청
            register_url = f"{self.base_url}/external/v2/products"
            body = json.dumps(product_data, ensure_ascii=False)
            headers = self._get_headers('POST', '/external/v2/products', body)
            
            async with self.session.post(register_url, data=body, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    product_id = result.get('originProductId')
                    logger.info(f"상품 등록 성공: {naver_product.product_name} (ID: {product_id})")
                    return product_id
                else:
                    error_data = await response.text()
                    logger.error(f"상품 등록 실패: {response.status} - {error_data}")
                    return None
                    
        except Exception as e:
            logger.error(f"상품 등록 오류: {str(e)}")
            return None
    
    async def batch_register_products(self, amazon_products: List[Dict]) -> Dict[str, Any]:
        """배치 상품 등록"""
        try:
            if not await self.authenticate():
                return {"error": "인증 실패"}
            
            results = {
                "total": len(amazon_products),
                "success": 0,
                "failed": 0,
                "success_products": [],
                "failed_products": []
            }
            
            for i, amazon_product in enumerate(amazon_products):
                try:
                    logger.info(f"상품 등록 진행: {i+1}/{len(amazon_products)} - {amazon_product.get('title', '')[:50]}")
                    
                    # 아마존 데이터를 네이버 형식으로 변환
                    naver_product = self.convert_amazon_to_naver_product(amazon_product)
                    
                    # 상품 등록
                    product_id = await self.register_product(naver_product)
                    
                    if product_id:
                        results["success"] += 1
                        results["success_products"].append({
                            "product_name": naver_product.product_name,
                            "product_id": product_id,
                            "price": naver_product.price
                        })
                    else:
                        results["failed"] += 1
                        results["failed_products"].append({
                            "product_name": amazon_product.get('title', ''),
                            "reason": "등록 실패"
                        })
                    
                    # API 요청 간격
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    results["failed"] += 1
                    results["failed_products"].append({
                        "product_name": amazon_product.get('title', ''),
                        "reason": str(e)
                    })
                    logger.error(f"개별 상품 등록 오류: {str(e)}")
            
            logger.info(f"배치 등록 완료 - 성공: {results['success']}, 실패: {results['failed']}")
            return results
            
        except Exception as e:
            logger.error(f"배치 등록 오류: {str(e)}")
            return {"error": str(e)}
    
    async def close(self):
        """세션 종료"""
        if self.session:
            await self.session.close()

class NaverRegistrationManager:
    """네이버 등록 관리자"""

    def __init__(self, config_file: str = None):
        """
        설정 로드

        Args:
            config_file: (더 이상 사용하지 않음) 하위 호환성을 위해 유지
        """
        if config_file:
            logger.warning(
                "⚠️  config_file 파라미터는 더 이상 사용되지 않습니다. "
                "환경 변수(.env)를 사용하세요."
            )

        self.config = self._load_config()
        self.api = None
    
    def _load_config(self) -> Dict:
        """
        환경 변수에서 설정 로드

        Returns:
            설정 딕셔너리
        """
        try:
            # SecureConfigLoader 사용
            if SecureConfigLoader:
                config_loader = SecureConfigLoader()

                # 네이버 API 설정 가져오기
                try:
                    naver_config = config_loader.get_naver_config()

                    return {
                        "naver_client_id": naver_config['client_id'],
                        "naver_client_secret": naver_config['client_secret'],
                        "naver_customer_id": naver_config['customer_id'],
                        "auto_register": config_loader.get('AUTO_REGISTER', 'false').lower() == 'true',
                        "max_daily_registrations": int(config_loader.get('MAX_DAILY_REGISTRATIONS', '100')),
                        "profit_margin_threshold": int(config_loader.get('PROFIT_MARGIN_THRESHOLD', '30'))
                    }
                except ValueError as e:
                    logger.error(f"환경 변수 설정 오류: {e}")
                    logger.error("💡 .env 파일을 확인하고 필수 환경 변수를 설정해주세요")
                    raise

            # 폴백: 환경 변수 직접 읽기
            else:
                logger.warning("SecureConfigLoader를 사용할 수 없습니다. 환경 변수를 직접 읽습니다.")

                client_id = os.getenv('NAVER_CLIENT_ID')
                client_secret = os.getenv('NAVER_CLIENT_SECRET')
                customer_id = os.getenv('NAVER_CUSTOMER_ID')

                if not all([client_id, client_secret, customer_id]):
                    raise ValueError(
                        "필수 환경 변수가 설정되지 않았습니다: "
                        "NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NAVER_CUSTOMER_ID\n"
                        ".env 파일을 생성하고 실제 값을 입력해주세요"
                    )

                return {
                    "naver_client_id": client_id,
                    "naver_client_secret": client_secret,
                    "naver_customer_id": customer_id,
                    "auto_register": os.getenv('AUTO_REGISTER', 'false').lower() == 'true',
                    "max_daily_registrations": int(os.getenv('MAX_DAILY_REGISTRATIONS', '100')),
                    "profit_margin_threshold": int(os.getenv('PROFIT_MARGIN_THRESHOLD', '30'))
                }

        except Exception as e:
            logger.error(f"설정 로드 오류: {str(e)}")
            raise
    
    async def initialize(self):
        """API 클라이언트 초기화"""
        self.api = NaverSmartStoreAPI(
            client_id=self.config.get('naver_client_id'),
            client_secret=self.config.get('naver_client_secret'),
            customer_id=self.config.get('naver_customer_id')
        )
        
        await self.api.init_session()
    
    async def register_amazon_products(self, amazon_products: List[Dict]) -> Dict:
        """아마존 상품들을 네이버에 등록"""
        try:
            await self.initialize()
            
            # 수익성 필터링
            filtered_products = []
            for product in amazon_products:
                if product.get('profit_margin', 0) >= self.config.get('profit_margin_threshold', 30):
                    filtered_products.append(product)
            
            logger.info(f"수익성 기준 통과 상품: {len(filtered_products)}개")
            
            # 일일 등록 제한 확인
            max_registrations = self.config.get('max_daily_registrations', 100)
            if len(filtered_products) > max_registrations:
                filtered_products = filtered_products[:max_registrations]
                logger.info(f"일일 등록 제한으로 {max_registrations}개만 등록")
            
            # 배치 등록 실행
            results = await self.api.batch_register_products(filtered_products)
            
            # 결과 저장
            await self._save_registration_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"네이버 등록 오류: {str(e)}")
            return {"error": str(e)}
        finally:
            if self.api:
                await self.api.close()
    
    async def _save_registration_results(self, results: Dict):
        """등록 결과 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = Path("C:/Users/PC8/Desktop/claude/아마존 크롤링") / f"naver_registration_results_{timestamp}.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"등록 결과 저장: {results_file}")
            
        except Exception as e:
            logger.error(f"결과 저장 오류: {str(e)}")

async def main():
    """테스트 실행"""
    # 샘플 아마존 상품 데이터
    sample_products = [
        {
            "title": "Optimum Nutrition Gold Standard 100% Whey Protein Powder",
            "price_usd": 45.99,
            "category": "protein powder",
            "brand": "Optimum Nutrition",
            "rating": 4.5,
            "review_count": 15000,
            "bsr_rank": 5,
            "image_url": "https://example.com/protein.jpg",
            "description": "Premium whey protein powder for muscle building",
            "profit_margin": 35.5
        }
    ]
    
    manager = NaverRegistrationManager()
    results = await manager.register_amazon_products(sample_products)
    
    print("="*50)
    print("🛒 네이버 스마트스토어 등록 결과")
    print("="*50)
    print(f"총 상품: {results.get('total', 0)}개")
    print(f"등록 성공: {results.get('success', 0)}개")
    print(f"등록 실패: {results.get('failed', 0)}개")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())