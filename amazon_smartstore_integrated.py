#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아마존 크롤링 + 스마트스토어 변환 통합 프로그램
원클릭으로 크롤링부터 스마트스토어 등록 파일 생성까지

작성일: 2025년 8월 1일
버전: v1.0 - 통합 버전
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import threading
import json
import os
import sys
import webbrowser
import subprocess
from datetime import datetime
import pandas as pd
import time
import random
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 필요한 모듈들 임포트
try:
    from amazon_crawler_selenium_improved import ImprovedAmazonCrawler
    from enhanced_smartstore_uploader import EnhancedSmartstoreUploader
    from korean_market_categories import KoreanMarketCategories
    print("[OK] 모든 필수 모듈 로드 완료 (개선된 버전)")
except ImportError as e:
    print(f"[ERROR] 필요한 모듈을 찾을 수 없습니다: {e}")
    print("패키지 설치가 필요할 수 있습니다.")
    
    # 패키지 자동 설치 시도
    try:
        from package_installer import PackageInstaller
        print("\n[INFO] 패키지 자동 설치를 시도합니다...")
        installer = PackageInstaller()
        success, results = installer.install_all()
        
        if success:
            print("[OK] 패키지 설치 완료. 프로그램을 다시 시작해주세요.")
        else:
            print("[ERROR] 일부 패키지 설치 실패. 수동 설치가 필요합니다.")
            print("pip install -r requirements.txt 명령어를 실행해주세요.")
    
    except Exception as install_error:
        print(f"[ERROR] 자동 설치 실패: {install_error}")
        print("수동으로 다음 명령어를 실행해주세요:")
        print("pip install -r requirements.txt")

class AmazonSmartstoreIntegrated:
    """아마존 크롤링 + 스마트스토어 변환 통합 GUI"""
    
    def __init__(self, root):
        self.root = root
        
        # 카테고리 시스템 먼저 초기화
        self.category_manager = KoreanMarketCategories()
        self.selected_categories = []  # 선택된 카테고리들
        
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.load_config()
        
        # 크롤링 및 변환 관련 변수
        self.crawler = None
        self.converter = None
        self.is_running = False
        self.crawled_products = []
        self.latest_crawl_file = None
        self.latest_smartstore_file = None
        
    def setup_window(self):
        """메인 윈도우 설정"""
        self.root.title("🛒 아마존 → 스마트스토어 통합 시스템 v1.0")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # 아이콘 설정 (선택사항)
        try:
            self.root.iconbitmap(default="amazon.ico")
        except:
            pass
            
        # 종료 시 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_variables(self):
        """tkinter 변수들 초기화"""
        # 기본 카테고리 선택 (추천 카테고리 상위 3개)
        recommended_categories = self.category_manager.get_recommended_categories(3)
        self.selected_categories = list(recommended_categories.keys())
        
        # 선택된 카테고리로부터 키워드 생성
        self.search_keywords = self.category_manager.get_category_mix_keywords(
            self.selected_categories, max_keywords_per_category=4
        )
        
        # 크롤링 설정
        self.products_per_keyword = tk.StringVar(value="20")
        self.crawl_delay = tk.StringVar(value="3")
        self.min_rating = tk.StringVar(value="3.0")
        self.min_reviews = tk.StringVar(value="10")
        
        # 스마트스토어 설정
        self.margin_rate = tk.StringVar(value="50")
        self.auto_convert = tk.BooleanVar(value=True)  # 크롤링 후 자동 변환
        self.enable_translation = tk.BooleanVar(value=True)  # 한국어 번역 활성화
        
        # 진행상황 변수
        self.progress_var = tk.StringVar(value="준비 완료")
        self.progress_detail = tk.StringVar(value="설정을 확인하고 시작 버튼을 클릭하세요")
        
        # 워크플로우 상태
        self.workflow_status = {
            'crawling': 'pending',  # pending, running, completed, failed
            'conversion': 'pending'
        }
    
    def create_widgets(self):
        """GUI 위젯들 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 탭 컨트롤 생성
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 탭 1: 워크플로우 (메인)
        self.create_workflow_tab(notebook)
        
        # 탭 2: 크롤링 설정
        self.create_crawling_tab(notebook)
        
        # 탭 3: 스마트스토어 설정
        self.create_smartstore_tab(notebook)
        
        # 탭 4: 진행상황 및 로그
        self.create_progress_tab(notebook)
        
        # 하단 제어 버튼들
        self.create_control_buttons(main_frame)
        
        # 상태바
        self.create_status_bar(main_frame)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_workflow_tab(self, notebook):
        """워크플로우 탭 (메인 대시보드)"""
        workflow_frame = ttk.Frame(notebook, padding="10")
        notebook.add(workflow_frame, text="🎯 워크플로우")
        
        # 제목
        title_label = ttk.Label(workflow_frame, text="🛒 아마존 → 스마트스토어 자동화 시스템", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 워크플로우 단계 표시
        steps_frame = ttk.LabelFrame(workflow_frame, text="📋 작업 단계", padding="15")
        steps_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 단계 1: 크롤링
        step1_frame = ttk.Frame(steps_frame)
        step1_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        steps_frame.columnconfigure(0, weight=1)
        
        self.step1_icon = ttk.Label(step1_frame, text="⏳", font=('Arial', 16))
        self.step1_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        step1_text = ttk.Frame(step1_frame)
        step1_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(step1_text, text="1단계: 아마존 상품 크롤링", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        self.step1_detail = ttk.Label(step1_text, text="설정된 키워드로 아마존에서 상품 정보 수집")
        self.step1_detail.pack(anchor=tk.W)
        
        # 구분선
        ttk.Separator(steps_frame, orient='horizontal').grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 단계 2: 변환
        step2_frame = ttk.Frame(steps_frame)
        step2_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.step2_icon = ttk.Label(step2_frame, text="⏳", font=('Arial', 16))
        self.step2_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        step2_text = ttk.Frame(step2_frame)
        step2_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(step2_text, text="2단계: 스마트스토어 파일 생성", 
                 font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        self.step2_detail = ttk.Label(step2_text, text="크롤링 데이터를 스마트스토어 등록 형식으로 변환")
        self.step2_detail.pack(anchor=tk.W)
        
        # 자동 변환 설정
        auto_frame = ttk.LabelFrame(workflow_frame, text="🔄 자동화 설정", padding="10")
        auto_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(auto_frame, text="크롤링 완료 후 자동으로 스마트스토어 파일 생성", 
                       variable=self.auto_convert).pack(anchor=tk.W, pady=5)
        
        # 카테고리 선택 (메인 기능으로 변경)
        category_frame = ttk.LabelFrame(workflow_frame, text="🏪 한국 인기 카테고리 선택", padding="10")
        category_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 카테고리 선택과 미리보기를 가로로 배치
        category_container = ttk.Frame(category_frame)
        category_container.pack(fill=tk.X)
        
        # 왼쪽: 카테고리 선택
        category_left = ttk.Frame(category_container)
        category_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(category_left, text="판매하고 싶은 상품 카테고리를 선택하세요:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # 카테고리 체크박스들 생성
        self.category_vars = {}
        self.category_checkboxes = {}
        
        # 스크롤 가능한 프레임 생성
        category_scroll_frame = ttk.Frame(category_left)
        category_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 카테고리 목록 생성
        categories_display = self.category_manager.get_categories_for_display()
        row = 0
        col = 0
        for category_info in categories_display:
            cat_id = category_info['id']
            
            # 체크박스 변수 생성
            var = tk.BooleanVar()
            # 기본 선택된 카테고리 설정
            if cat_id in self.selected_categories:
                var.set(True)
            self.category_vars[cat_id] = var
            
            # 체크박스와 정보 표시
            checkbox_frame = ttk.Frame(category_scroll_frame)
            checkbox_frame.grid(row=row, column=col, sticky=(tk.W, tk.E), padx=5, pady=2)
            
            checkbox = ttk.Checkbutton(
                checkbox_frame, 
                text=f"{category_info['name']} (인기도 {category_info['popularity']}%)",
                variable=var,
                command=self.on_category_selection_changed
            )
            checkbox.pack(anchor=tk.W)
            
            # 설명 텍스트
            desc_label = ttk.Label(
                checkbox_frame, 
                text=f"   💰 마진: {category_info['profit_margin']}% | 키워드: {category_info['keyword_count']}개",
                font=('Arial', 8),
                foreground='gray'
            )
            desc_label.pack(anchor=tk.W)
            
            self.category_checkboxes[cat_id] = checkbox
            
            col += 1
            if col > 1:  # 2열로 배치
                col = 0
                row += 1
        
        # 오른쪽: 선택된 카테고리 미리보기
        category_right = ttk.Frame(category_container)
        category_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(category_right, text="선택된 키워드 미리보기:", font=('Arial', 9, 'bold')).pack(pady=(0, 5))
        
        # 키워드 미리보기 리스트박스
        self.keyword_preview_listbox = tk.Listbox(category_right, height=10, width=30, font=('Arial', 8))
        self.keyword_preview_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 카테고리 관리 버튼들
        category_buttons = ttk.Frame(category_right)
        category_buttons.pack(pady=(5, 0), fill=tk.X)
        
        ttk.Button(category_buttons, text="🎯 추천 선택", width=12, 
                  command=self.select_recommended_categories).pack(pady=1, fill=tk.X)
        ttk.Button(category_buttons, text="✅ 전체 선택", width=12, 
                  command=self.select_all_categories).pack(pady=1, fill=tk.X)
        ttk.Button(category_buttons, text="❌ 전체 해제", width=12, 
                  command=self.deselect_all_categories).pack(pady=1, fill=tk.X)
        
        # 초기 키워드 미리보기 업데이트
        self.update_keyword_preview()
        
        # 빠른 설정
        quick_frame = ttk.LabelFrame(workflow_frame, text="⚡ 빠른 설정", padding="10")
        quick_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        settings_grid = ttk.Frame(quick_frame)
        settings_grid.pack(fill=tk.X)
        
        # 상품 수
        ttk.Label(settings_grid, text="키워드당 상품 수:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(settings_grid, textvariable=self.products_per_keyword, width=8).grid(row=0, column=1, padx=5)
        
        # 마진율
        ttk.Label(settings_grid, text="판매 마진율 (%):").grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Entry(settings_grid, textvariable=self.margin_rate, width=8).grid(row=0, column=3, padx=5)
        
        # 추가 설정들
        ttk.Label(settings_grid, text="최소 평점:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=(5,0))
        ttk.Entry(settings_grid, textvariable=self.min_rating, width=8).grid(row=1, column=1, padx=5, pady=(5,0))
        
        ttk.Label(settings_grid, text="최소 리뷰 수:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=(5,0))
        ttk.Entry(settings_grid, textvariable=self.min_reviews, width=8).grid(row=1, column=3, padx=5, pady=(5,0))
        
        # 번역 설정 추가
        translation_frame = ttk.Frame(settings_grid)
        translation_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10,0))
        
        ttk.Checkbutton(translation_frame, text="🌐 한국어 자동 번역 (제목 + 설명)", 
                       variable=self.enable_translation).pack(side=tk.LEFT)
        
        # 번역 안내 라벨
        translation_info = ttk.Label(translation_frame, text="✨ 영어 상품명과 설명을 한국어로 자동 번역합니다", 
                                   foreground="gray")
        translation_info.pack(side=tk.LEFT, padx=(20,0))
        
        # 최근 결과 표시
        results_frame = ttk.LabelFrame(workflow_frame, text="📊 최근 결과", padding="10")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.results_text = ttk.Label(results_frame, text="아직 실행한 결과가 없습니다.", 
                                     foreground='gray')
        self.results_text.pack(anchor=tk.W)
    
    def create_crawling_tab(self, notebook):
        """크롤링 설정 탭"""
        crawling_frame = ttk.Frame(notebook, padding="10")
        notebook.add(crawling_frame, text="🕷️ 크롤링 설정")
        
        # 검색 키워드 설정
        keywords_frame = ttk.LabelFrame(crawling_frame, text="🔍 검색 키워드", padding="10")
        keywords_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 키워드 목록 표시
        self.keywords_listbox = tk.Listbox(keywords_frame, height=8)
        self.keywords_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 초기 키워드 로드
        for keyword in self.search_keywords:
            self.keywords_listbox.insert(tk.END, keyword)
        
        # 키워드 관리 버튼들
        keyword_buttons = ttk.Frame(keywords_frame)
        keyword_buttons.grid(row=0, column=1, sticky=(tk.N))
        
        ttk.Button(keyword_buttons, text="추가", command=self.add_keyword).pack(pady=2, fill=tk.X)
        ttk.Button(keyword_buttons, text="삭제", command=self.remove_keyword).pack(pady=2, fill=tk.X)
        ttk.Button(keyword_buttons, text="편집", command=self.edit_keyword).pack(pady=2, fill=tk.X)
        
        keywords_frame.columnconfigure(0, weight=1)
        
        # 크롤링 설정
        settings_frame = ttk.LabelFrame(crawling_frame, text="⚙️ 크롤링 설정", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(settings_frame, text="키워드당 최대 상품 수:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.products_per_keyword, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="요청 간격 (초):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.crawl_delay, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="최소 평점:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.min_rating, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="최소 리뷰 수:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.min_reviews, width=10).grid(row=3, column=1, padx=5, pady=5)
        
        crawling_frame.columnconfigure(0, weight=1)
    
    def create_smartstore_tab(self, notebook):
        """스마트스토어 설정 탭"""
        smartstore_frame = ttk.Frame(notebook, padding="10")
        notebook.add(smartstore_frame, text="🏪 스마트스토어 설정")
        
        # 가격 설정
        price_frame = ttk.LabelFrame(smartstore_frame, text="💰 가격 및 마진 설정", padding="10")
        price_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(price_frame, text="판매 마진율 (%):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(price_frame, textvariable=self.margin_rate, width=10).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(price_frame, text="예: 50% = 원가의 1.5배로 판매", font=('Arial', 8), 
                 foreground='gray').grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 비용 계산 정보
        cost_info = """
💡 자동 계산 항목:
• USD → KRW 환율 변환 (1,350원/USD)
• 국제배송비 (상품가의 10%, 최대 20,000원)
• 관세 (8%)
• 플랫폼 수수료 (3%)
• 운영비 (5%)
• 설정한 마진율
        """
        
        info_frame = ttk.LabelFrame(smartstore_frame, text="📊 가격 계산 방식", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, state='disabled')
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(0, weight=1)
        
        info_text.config(state='normal')
        info_text.insert(tk.END, cost_info.strip())
        info_text.config(state='disabled')
        
        # 카테고리 매핑 정보
        category_frame = ttk.LabelFrame(smartstore_frame, text="🏷️ 카테고리 매핑", padding="10")
        category_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        category_info = """
아마존 카테고리 → 스마트스토어 카테고리:
• protein powder → 건강기능식품 > 단백질보충제
• vitamins → 건강기능식품 > 비타민/미네랄
• supplements → 건강기능식품 > 건강보조식품
• baby products → 출산/육아 > 베이비용품
• kitchen gadgets → 생활용품 > 주방용품
        """
        
        category_text = tk.Text(category_frame, height=6, wrap=tk.WORD, state='disabled')
        category_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        category_frame.columnconfigure(0, weight=1)
        
        category_text.config(state='normal')
        category_text.insert(tk.END, category_info.strip())
        category_text.config(state='disabled')
        
        smartstore_frame.columnconfigure(0, weight=1)
    
    def create_progress_tab(self, notebook):
        """진행상황 탭"""
        progress_frame = ttk.Frame(notebook, padding="10")
        notebook.add(progress_frame, text="📊 진행상황")
        
        # 현재 상태 표시
        status_group = ttk.LabelFrame(progress_frame, text="📈 현재 상태", padding="10")
        status_group.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(status_group, textvariable=self.progress_var, 
                                       font=('Arial', 11, 'bold'))
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_detail_label = ttk.Label(status_group, textvariable=self.progress_detail)
        self.progress_detail_label.grid(row=1, column=0, sticky=tk.W)
        
        # 프로그레스 바
        self.progress_bar = ttk.Progressbar(status_group, mode='indeterminate')
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 로그 창
        log_group = ttk.LabelFrame(progress_frame, text="📝 실행 로그", padding="10")
        log_group.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_group, height=20, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 로그 버튼들
        log_buttons = ttk.Frame(log_group)
        log_buttons.grid(row=1, column=0, pady=5)
        
        ttk.Button(log_buttons, text="로그 지우기", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_buttons, text="로그 저장", 
                  command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # 그리드 가중치
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        status_group.columnconfigure(0, weight=1)
        log_group.columnconfigure(0, weight=1)
        log_group.rowconfigure(0, weight=1)
    
    def create_control_buttons(self, parent):
        """제어 버튼들"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 메인 실행 버튼 (크고 눈에 띄게)
        self.start_button = ttk.Button(button_frame, text="🚀 전체 워크플로우 시작", 
                                      command=self.start_full_workflow, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # 중지 버튼
        self.stop_button = ttk.Button(button_frame, text="⏹️ 중지", 
                                     command=self.stop_workflow, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 개별 실행 버튼들
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        self.crawl_only_button = ttk.Button(button_frame, text="🕷️ 크롤링만", 
                                           command=self.start_crawling_only)
        self.crawl_only_button.pack(side=tk.LEFT, padx=5)
        
        self.convert_only_button = ttk.Button(button_frame, text="🏪 변환만", 
                                             command=self.start_conversion_only, state='disabled')
        self.convert_only_button.pack(side=tk.LEFT, padx=5)
        
        # 기타 버튼들
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(button_frame, text="📁 폴더 열기", 
                  command=self.open_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❓ 도움말", 
                  command=self.show_help).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """상태바"""
        self.status_bar = ttk.Label(parent, text="준비 완료 - 전체 워크플로우를 시작하세요", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
    
    # 키워드 관리 함수들
    def add_keyword(self):
        """키워드 추가"""
        keyword = tk.simpledialog.askstring("키워드 추가", "추가할 검색 키워드를 입력하세요:")
        if keyword and keyword.strip():
            self.keywords_listbox.insert(tk.END, keyword.strip())
            self.search_keywords.append(keyword.strip())
    
    def remove_keyword(self):
        """키워드 삭제"""
        selection = self.keywords_listbox.curselection()
        if selection:
            index = selection[0]
            self.keywords_listbox.delete(index)
            if index < len(self.search_keywords):
                del self.search_keywords[index]
    
    def edit_keyword(self):
        """키워드 편집"""
        selection = self.keywords_listbox.curselection()
        if selection:
            index = selection[0]
            current = self.keywords_listbox.get(index)
            new_keyword = tk.simpledialog.askstring("키워드 편집", "키워드를 수정하세요:", initialvalue=current)
            if new_keyword and new_keyword.strip():
                self.keywords_listbox.delete(index)
                self.keywords_listbox.insert(index, new_keyword.strip())
                self.search_keywords[index] = new_keyword.strip()
    
    # 카테고리 관리 함수들
    def on_category_selection_changed(self):
        """카테고리 선택이 변경될 때 호출"""
        # 선택된 카테고리 목록 업데이트
        self.selected_categories = []
        for cat_id, var in self.category_vars.items():
            if var.get():
                self.selected_categories.append(cat_id)
        
        # 키워드 목록 업데이트
        if self.selected_categories:
            self.search_keywords = self.category_manager.get_category_mix_keywords(
                self.selected_categories, max_keywords_per_category=4
            )
        else:
            self.search_keywords = []
        
        # 키워드 미리보기 업데이트
        self.update_keyword_preview()
        
        # 크롤링 설정 탭의 키워드 리스트박스도 업데이트
        if hasattr(self, 'keywords_listbox'):
            self.keywords_listbox.delete(0, tk.END)
            for keyword in self.search_keywords:
                self.keywords_listbox.insert(tk.END, keyword)
    
    def update_keyword_preview(self):
        """키워드 미리보기 업데이트"""
        self.keyword_preview_listbox.delete(0, tk.END)
        
        if not self.selected_categories:
            self.keyword_preview_listbox.insert(tk.END, "카테고리를 선택해주세요")
            return
        
        # 카테고리별로 그룹화하여 표시
        for cat_id in self.selected_categories:
            category_info = self.category_manager.get_category_info(cat_id)
            if category_info:
                # 카테고리 헤더
                self.keyword_preview_listbox.insert(tk.END, f"📂 {category_info['name']}")
                
                # 해당 카테고리의 키워드들 (최대 4개)
                keywords = category_info['keywords'][:4]
                for keyword in keywords:
                    self.keyword_preview_listbox.insert(tk.END, f"  • {keyword}")
                
                # 구분선
                if cat_id != self.selected_categories[-1]:  # 마지막이 아니면
                    self.keyword_preview_listbox.insert(tk.END, "")
        
        # 총 키워드 수 표시
        total_keywords = len(self.search_keywords)
        self.keyword_preview_listbox.insert(tk.END, "")
        self.keyword_preview_listbox.insert(tk.END, f"🎯 총 {total_keywords}개 키워드 사용")
    
    def select_recommended_categories(self):
        """추천 카테고리 선택"""
        # 모든 카테고리 해제
        for var in self.category_vars.values():
            var.set(False)
        
        # 추천 카테고리 선택 (상위 3개)
        recommended = self.category_manager.get_recommended_categories(3)
        for cat_id in recommended.keys():
            if cat_id in self.category_vars:
                self.category_vars[cat_id].set(True)
        
        # 선택 변경 이벤트 호출
        self.on_category_selection_changed()
        self.log_message("추천 카테고리가 선택되었습니다.")
    
    def select_all_categories(self):
        """모든 카테고리 선택"""
        for var in self.category_vars.values():
            var.set(True)
        self.on_category_selection_changed()
        self.log_message("모든 카테고리가 선택되었습니다.")
    
    def deselect_all_categories(self):
        """모든 카테고리 해제"""
        for var in self.category_vars.values():
            var.set(False)
        self.on_category_selection_changed()
        self.log_message("모든 카테고리 선택이 해제되었습니다.")
    
    # 워크플로우 실행 함수들
    def start_full_workflow(self):
        """전체 워크플로우 시작 (크롤링 + 변환)"""
        if self.is_running:
            return
        
        # 설정 검증
        try:
            self.validate_settings()
        except ValueError as e:
            messagebox.showerror("설정 오류", str(e))
            return
        
        self.is_running = True
        self.update_ui_running_state(True)
        self.clear_log()
        
        self.log_message("🚀 전체 워크플로우를 시작합니다...")
        self.log_message(f"📝 검색 키워드: {', '.join(self.search_keywords)}")
        self.log_message(f"⚙️ 키워드당 상품 수: {self.products_per_keyword.get()}개")
        self.log_message(f"💰 판매 마진율: {self.margin_rate.get()}%")
        
        # 별도 쓰레드에서 워크플로우 실행
        self.workflow_thread = threading.Thread(target=self.run_full_workflow)
        self.workflow_thread.daemon = True
        self.workflow_thread.start()
    
    def start_crawling_only(self):
        """크롤링만 실행"""
        if self.is_running:
            return
        
        try:
            self.validate_crawling_settings()
        except ValueError as e:
            messagebox.showerror("설정 오류", str(e))
            return
        
        self.is_running = True
        self.update_ui_running_state(True)
        self.clear_log()
        
        self.log_message("🕷️ 아마존 크롤링을 시작합니다...")
        
        # 별도 쓰레드에서 크롤링만 실행
        self.crawling_thread = threading.Thread(target=self.run_crawling_only)
        self.crawling_thread.daemon = True
        self.crawling_thread.start()
    
    def start_conversion_only(self):
        """변환만 실행"""
        if not self.latest_crawl_file or not os.path.exists(self.latest_crawl_file):
            messagebox.showwarning("경고", "변환할 크롤링 파일이 없습니다.\n먼저 크롤링을 실행해주세요.")
            return
        
        try:
            margin_rate = int(self.margin_rate.get())
            if margin_rate < 10 or margin_rate > 200:
                raise ValueError("마진율은 10% ~ 200% 사이여야 합니다.")
        except ValueError as e:
            messagebox.showerror("설정 오류", str(e))
            return
        
        self.log_message("🏪 스마트스토어 변환을 시작합니다...")
        
        # 별도 쓰레드에서 변환만 실행
        self.conversion_thread = threading.Thread(target=self.run_conversion_only)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
    
    def run_full_workflow(self):
        """전체 워크플로우 실행 (별도 쓰레드)"""
        try:
            # 1단계: 크롤링
            self.update_workflow_step(1, 'running')
            self.update_progress("1단계 실행 중", "아마존에서 상품 정보를 수집하고 있습니다...")
            
            success = self.execute_crawling()
            if not success:
                self.update_workflow_step(1, 'failed')
                raise Exception("크롤링에 실패했습니다.")
            
            self.update_workflow_step(1, 'completed')
            self.log_message(f"✅ 1단계 완료: {len(self.crawled_products)}개 상품 수집")
            
            # 자동 변환이 설정된 경우에만 2단계 실행
            if self.auto_convert.get():
                time.sleep(2)  # 잠깐 대기
                
                # 2단계: 변환
                self.update_workflow_step(2, 'running')
                self.update_progress("2단계 실행 중", "스마트스토어 등록 파일을 생성하고 있습니다...")
                
                success = self.execute_conversion()
                if not success:
                    self.update_workflow_step(2, 'failed')
                    raise Exception("스마트스토어 변환에 실패했습니다.")
                
                self.update_workflow_step(2, 'completed')
                self.log_message("✅ 2단계 완료: 스마트스토어 파일 생성")
            
            # 완료 처리
            self.root.after(0, self.on_workflow_complete)
            
        except Exception as e:
            error_msg = f"워크플로우 오류: {e}"
            self.log_message(f"❌ {error_msg}")
            self.update_progress("오류 발생", error_msg)
            self.root.after(0, lambda: self.on_workflow_error(str(e)))
    
    def run_crawling_only(self):
        """크롤링만 실행 (별도 쓰레드)"""
        try:
            self.update_workflow_step(1, 'running')
            self.update_progress("크롤링 중", "아마존에서 상품 정보를 수집하고 있습니다...")
            
            success = self.execute_crawling()
            if not success:
                raise Exception("크롤링에 실패했습니다.")
            
            self.update_workflow_step(1, 'completed')
            self.log_message(f"✅ 크롤링 완료: {len(self.crawled_products)}개 상품 수집")
            
            self.root.after(0, self.on_crawling_complete)
            
        except Exception as e:
            self.update_workflow_step(1, 'failed')
            error_msg = f"크롤링 오류: {e}"
            self.log_message(f"❌ {error_msg}")
            self.update_progress("크롤링 실패", error_msg)
            self.root.after(0, lambda: self.on_workflow_error(str(e)))
    
    def run_conversion_only(self):
        """변환만 실행 (별도 쓰레드)"""
        try:
            self.update_workflow_step(2, 'running')
            self.update_progress("변환 중", "스마트스토어 등록 파일을 생성하고 있습니다...")
            
            success = self.execute_conversion()
            if not success:
                raise Exception("스마트스토어 변환에 실패했습니다.")
            
            self.update_workflow_step(2, 'completed')
            self.log_message("✅ 변환 완료: 스마트스토어 파일 생성")
            
            self.root.after(0, self.on_conversion_complete)
            
        except Exception as e:
            self.update_workflow_step(2, 'failed')
            error_msg = f"변환 오류: {e}"
            self.log_message(f"❌ {error_msg}")
            self.update_progress("변환 실패", error_msg)
            self.root.after(0, lambda: self.on_workflow_error(str(e)))
    
    def execute_crawling(self):
        """실제 크롤링 실행"""
        try:
            # Selenium 크롤러 설정
            config = {
                "crawler_settings": {
                    "max_products_per_keyword": int(self.products_per_keyword.get()),
                    "min_rating": float(self.min_rating.get()),
                    "min_reviews": int(self.min_reviews.get()),
                    "crawl_delay": int(self.crawl_delay.get())
                }
            }
            
            # 설정 파일 임시 저장
            with open('temp_crawl_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 개선된 크롤러 초기화 및 실행
            crawler = ImprovedAmazonCrawler('temp_crawl_config.json')
            crawler.search_keywords = self.search_keywords.copy()
            
            products = crawler.crawl_all_keywords()
            
            if products:
                self.crawled_products = products
                
                # 결과 파일 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_filename = f"amazon_products_integrated_{timestamp}.json"
                csv_filename = f"amazon_products_integrated_{timestamp}.csv"
                
                # JSON 저장
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                
                # CSV 저장
                df = pd.DataFrame(products)
                df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
                
                self.latest_crawl_file = json_filename
                self.log_message(f"📁 크롤링 결과 저장: {json_filename}")
                
                return True
            else:
                return False
                
        except Exception as e:
            self.log_message(f"❌ 크롤링 실행 오류: {e}")
            return False
        finally:
            # 임시 파일 정리
            try:
                os.remove('temp_crawl_config.json')
            except:
                pass
    
    def execute_conversion(self):
        """실제 변환 실행 (안전한 에러 처리)"""
        try:
            if not self.latest_crawl_file:
                self.log_message("❌ 크롤링 파일이 없습니다. 먼저 크롤링을 실행하세요.")
                return False
            
            if not os.path.exists(self.latest_crawl_file):
                self.log_message(f"❌ 크롤링 파일을 찾을 수 없습니다: {self.latest_crawl_file}")
                return False
            
            self.log_message("🔄 스마트스토어 변환 시작...")
            
            # 개선된 스마트스토어 업로더 초기화 (상세페이지 이미지 포함 버전)
            uploader = EnhancedSmartstoreUploader(enable_translation=self.enable_translation.get())
            
            # 변환 실행
            margin_rate = int(self.margin_rate.get())
            self.log_message(f"📊 마진율: {margin_rate}%")
            
            output_file = uploader.convert_file(
                input_file=self.latest_crawl_file
            )
            
            if output_file and os.path.exists(output_file):
                self.latest_smartstore_file = output_file
                self.log_message(f"✅ 스마트스토어 업로드 파일 생성 성공!")
                self.log_message(f"📁 파일 위치: {os.path.basename(output_file)}")
                self.log_message("📋 네이버 스마트스토어 일괄등록에서 사용 가능한 Excel 파일입니다.")
                
                # 참고용 파일 정보 추가
                reference_file = output_file.replace('.xlsx', '_참고용.xlsx')
                if os.path.exists(reference_file):
                    self.log_message(f"📊 참고용 상세 정보: {os.path.basename(reference_file)}")
                
                return True
            else:
                self.log_message("❌ 스마트스토어 파일 생성에 실패했습니다.")
                self.log_message("💡 가능한 원인: 데이터 품질 문제, 필수 필드 누락, 변환 오류")
                return False
                
        except Exception as e:
            # 에러 발생 시 로그만 출력하고 절대 파일을 생성하지 않음
            error_msg = str(e)
            self.log_message(f"❌ 변환 중 오류 발생: {error_msg}")
            self.log_message("💡 해결방법: 크롤링을 다시 실행하거나 데이터를 확인해주세요.")
            
            # 에러 파일 생성하지 않음 - 오직 로그만!
            return False
    
    # UI 업데이트 함수들
    def update_workflow_step(self, step, status):
        """워크플로우 단계 상태 업데이트"""
        icons = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }
        
        if step == 1:
            self.root.after(0, lambda: self.step1_icon.config(text=icons[status]))
            self.workflow_status['crawling'] = status
        elif step == 2:
            self.root.after(0, lambda: self.step2_icon.config(text=icons[status]))
            self.workflow_status['conversion'] = status
    
    def update_ui_running_state(self, running):
        """실행 중 UI 상태 업데이트"""
        self.start_button.config(state='disabled' if running else 'normal')
        self.crawl_only_button.config(state='disabled' if running else 'normal')
        self.stop_button.config(state='normal' if running else 'disabled')
        
        if running:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
    
    def update_progress(self, status, detail):
        """진행상황 업데이트 (쓰레드 안전)"""
        self.root.after(0, lambda: self._update_progress_ui(status, detail))
    
    def _update_progress_ui(self, status, detail):
        """UI 진행상황 업데이트"""
        self.progress_var.set(status)
        self.progress_detail.set(detail)
        self.status_bar.config(text=f"{status} - {detail}")
    
    def log_message(self, message):
        """로그 메시지 추가 (쓰레드 안전)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.root.after(0, lambda: self._add_log_message(formatted_message))
    
    def _add_log_message(self, message):
        """UI 로그 메시지 추가"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    # 완료 처리 함수들
    def on_workflow_complete(self):
        """전체 워크플로우 완료 처리"""
        self.is_running = False
        self.update_ui_running_state(False)
        self.convert_only_button.config(state='normal')
        
        # 결과 업데이트
        if self.auto_convert.get() and self.latest_smartstore_file:
            result_text = f"✅ 전체 워크플로우 완료!\n"
            result_text += f"• 수집 상품: {len(self.crawled_products)}개\n"
            result_text += f"• 스마트스토어 파일: {os.path.basename(self.latest_smartstore_file)}"
        else:
            result_text = f"✅ 크롤링 완료!\n"
            result_text += f"• 수집 상품: {len(self.crawled_products)}개\n"
            result_text += f"• 변환하려면 '변환만' 버튼을 클릭하세요"
        
        self.results_text.config(text=result_text, foreground='green')
        self.update_progress("완료!", "모든 작업이 성공적으로 완료되었습니다")
        
        # 완료 메시지
        if self.auto_convert.get() and self.latest_smartstore_file:
            result = messagebox.askyesno(
                "워크플로우 완료!",
                f"전체 워크플로우가 완료되었습니다!\n\n"
                f"📊 수집 상품: {len(self.crawled_products)}개\n"
                f"📁 스마트스토어 파일: {os.path.basename(self.latest_smartstore_file)}\n\n"
                f"스마트스토어 파일을 열어보시겠습니까?"
            )
            
            if result and self.latest_smartstore_file:
                try:
                    os.startfile(self.latest_smartstore_file)
                except:
                    messagebox.showinfo("알림", "파일을 수동으로 열어주세요.")
        else:
            messagebox.showinfo(
                "크롤링 완료!",
                f"아마존 상품 크롤링이 완료되었습니다!\n\n"
                f"📊 수집 상품: {len(self.crawled_products)}개\n\n"
                f"스마트스토어 변환을 원하시면 '변환만' 버튼을 클릭하세요."
            )
    
    def on_crawling_complete(self):
        """크롤링만 완료 처리"""
        self.is_running = False
        self.update_ui_running_state(False)
        self.convert_only_button.config(state='normal')
        
        result_text = f"✅ 크롤링 완료!\n"
        result_text += f"• 수집 상품: {len(self.crawled_products)}개\n"
        result_text += f"• 변환하려면 '변환만' 버튼을 클릭하세요"
        
        self.results_text.config(text=result_text, foreground='green')
        self.update_progress("크롤링 완료!", f"총 {len(self.crawled_products)}개 상품 수집 완료")
        
        messagebox.showinfo(
            "크롤링 완료!",
            f"아마존 상품 크롤링이 완료되었습니다!\n\n"
            f"📊 수집 상품: {len(self.crawled_products)}개\n\n"
            f"스마트스토어 변환을 원하시면 '변환만' 버튼을 클릭하세요."
        )
    
    def on_conversion_complete(self):
        """변환만 완료 처리"""
        result_text = f"✅ 변환 완료!\n"
        result_text += f"• 스마트스토어 파일: {os.path.basename(self.latest_smartstore_file)}"
        
        self.results_text.config(text=result_text, foreground='green')
        self.update_progress("변환 완료!", f"스마트스토어 파일 생성 완료")
        
        result = messagebox.askyesno(
            "변환 완료!",
            f"스마트스토어 파일 변환이 완료되었습니다!\n\n"
            f"📁 파일: {os.path.basename(self.latest_smartstore_file)}\n\n"
            f"파일을 열어보시겠습니까?"
        )
        
        if result and self.latest_smartstore_file:
            try:
                os.startfile(self.latest_smartstore_file)
            except:
                messagebox.showinfo("알림", "파일을 수동으로 열어주세요.")
    
    def on_workflow_error(self, error):
        """워크플로우 오류 처리"""
        self.is_running = False
        self.update_ui_running_state(False)
        
        self.results_text.config(text=f"❌ 오류 발생: {error}", foreground='red')
        messagebox.showerror("워크플로우 오류", f"작업 중 오류가 발생했습니다:\n{error}")
    
    def stop_workflow(self):
        """워크플로우 중지"""
        if self.is_running:
            self.is_running = False
            self.log_message("⏹️ 사용자가 작업을 중지했습니다.")
            self.update_ui_running_state(False)
            self.update_progress("중지됨", "사용자에 의해 작업이 중지되었습니다")
    
    # 설정 검증 함수들
    def validate_settings(self):
        """전체 설정 검증"""
        self.validate_crawling_settings()
        self.validate_smartstore_settings()
    
    def validate_crawling_settings(self):
        """크롤링 설정 검증"""
        try:
            products_per_keyword = int(self.products_per_keyword.get())
            crawl_delay = int(self.crawl_delay.get())
            min_rating = float(self.min_rating.get())
            min_reviews = int(self.min_reviews.get())
            
            if products_per_keyword < 1 or products_per_keyword > 50:
                raise ValueError("키워드당 상품 수는 1-50 사이여야 합니다.")
            if crawl_delay < 1:
                raise ValueError("요청 간격은 1초 이상이어야 합니다.")
            if not (0 <= min_rating <= 5):
                raise ValueError("최소 평점은 0-5 사이여야 합니다.")
            if min_reviews < 0:
                raise ValueError("최소 리뷰 수는 0 이상이어야 합니다.")
            if not self.search_keywords:
                raise ValueError("최소 하나의 검색 키워드가 필요합니다.")
                
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError("모든 설정값은 숫자여야 합니다.")
            raise e
    
    def validate_smartstore_settings(self):
        """스마트스토어 설정 검증"""
        try:
            margin_rate = int(self.margin_rate.get())
            if margin_rate < 10 or margin_rate > 200:
                raise ValueError("마진율은 10% ~ 200% 사이여야 합니다.")
        except ValueError as e:
            if "could not convert" in str(e):
                raise ValueError("마진율은 숫자여야 합니다.")
            raise e
    
    # 기타 유틸리티 함수들
    def load_config(self):
        """설정 로드"""
        try:
            if os.path.exists('integrated_config.json'):
                with open('integrated_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 설정 적용
                if 'search_keywords' in config:
                    self.search_keywords = config['search_keywords']
                    self.keywords_listbox.delete(0, tk.END)
                    for keyword in self.search_keywords:
                        self.keywords_listbox.insert(tk.END, keyword)
                
                if 'products_per_keyword' in config:
                    self.products_per_keyword.set(str(config['products_per_keyword']))
                if 'margin_rate' in config:
                    self.margin_rate.set(str(config['margin_rate']))
                if 'auto_convert' in config:
                    self.auto_convert.set(config['auto_convert'])
                if 'enable_translation' in config:
                    self.enable_translation.set(config['enable_translation'])
                    
        except Exception as e:
            self.log_message(f"설정 로드 실패: {e}")
    
    def save_config(self):
        """설정 저장"""
        try:
            config = {
                'search_keywords': self.search_keywords,
                'products_per_keyword': int(self.products_per_keyword.get()),
                'crawl_delay': int(self.crawl_delay.get()),
                'min_rating': float(self.min_rating.get()),
                'min_reviews': int(self.min_reviews.get()),
                'margin_rate': int(self.margin_rate.get()),
                'auto_convert': self.auto_convert.get(),
                'enable_translation': self.enable_translation.get()
            }
            
            with open('integrated_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_message(f"설정 저장 실패: {e}")
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """로그 저장"""
        log_content = self.log_text.get(1.0, tk.END)
        if not log_content.strip():
            messagebox.showwarning("경고", "저장할 로그가 없습니다.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"workflow_log_{timestamp}.txt"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            messagebox.showinfo("성공", f"로그가 저장되었습니다: {file_path}")
        except Exception as e:
            messagebox.showerror("오류", f"로그 저장 실패: {e}")
    
    def open_folder(self):
        """현재 폴더 열기"""
        try:
            os.startfile(current_dir)
        except:
            subprocess.run(['explorer', current_dir])
    
    def show_help(self):
        """도움말 표시"""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ 도움말")
        help_window.geometry("700x600")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
🛒 아마존 → 스마트스토어 통합 시스템 도움말

📋 주요 기능:
• 아마존 상품 자동 크롤링
• 스마트스토어 등록 파일 자동 생성
• 원클릭 전체 워크플로우 실행
• 개별 단계 실행 가능

🚀 사용 방법:

1️⃣ 전체 워크플로우 (권장):
   • '전체 워크플로우 시작' 버튼 클릭
   • 크롤링 → 자동 변환까지 원클릭 실행
   • 완료 후 스마트스토어 파일 자동 생성

2️⃣ 단계별 실행:
   • '크롤링만' 버튼: 아마존 상품 수집만
   • '변환만' 버튼: 기존 크롤링 파일을 스마트스토어 형식으로 변환

⚙️ 설정 가이드:

🔍 크롤링 설정:
• 키워드당 상품 수: 10-20개 권장
• 요청 간격: 3초 이상 (차단 방지)
• 최소 평점: 4.0 이상 권장
• 최소 리뷰 수: 50개 이상 권장

🏪 스마트스토어 설정:
• 판매 마진율: 40-60% 권장
• 자동 변환: 체크 시 크롤링 후 자동 변환

💰 가격 계산 방식:
1. 아마존 가격 (USD → KRW)
2. + 국제배송비 (10%, 최대 20,000원)
3. + 관세 (8%)
4. + 플랫폼 수수료 (3%)
5. + 운영비 (5%)
6. + 설정한 마진율

📊 결과 파일:
• JSON: 원본 크롤링 데이터
• CSV: 스프레드시트용 데이터
• XLSX: 스마트스토어 등록용 파일

⚠️ 주의사항:
• 아마존 이용약관 준수
• 과도한 요청으로 인한 IP 차단 주의
• 브랜드 권리 및 수입 규정 확인
• 생성된 파일은 참고용, 실제 판매 전 검토 필요

🔧 문제 해결:
• 크롤링 실패: 네트워크 연결 및 키워드 확인
• 변환 실패: 크롤링 파일 존재 여부 확인
• 속도 저하: 요청 간격 증가

📞 지원:
• 로그 파일에서 상세 오류 정보 확인
• README 파일 참조
• GitHub 이슈 등록

🎯 팁:
• 처음 사용 시 적은 수의 상품으로 테스트
• 마진율은 시장 조사 후 설정
• 정기적으로 설정 저장하여 재사용
        """
        
        help_text.insert(tk.END, help_content.strip())
        help_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """프로그램 종료 시"""
        if self.is_running:
            if messagebox.askokcancel("종료", "작업이 진행 중입니다. 정말 종료하시겠습니까?"):
                self.is_running = False
                self.save_config()  # 종료 전 설정 저장
                self.root.destroy()
        else:
            self.save_config()  # 종료 전 설정 저장
            self.root.destroy()

def main():
    """메인 함수"""
    # tkinter 루트 윈도우 생성
    root = tk.Tk()
    
    # 스타일 설정
    style = ttk.Style()
    try:
        style.theme_use('clam')  # 모던한 테마
    except:
        pass
    
    # GUI 앱 생성
    app = AmazonSmartstoreIntegrated(root)
    
    # 메인 루프 시작
    root.mainloop()

if __name__ == "__main__":
    main()