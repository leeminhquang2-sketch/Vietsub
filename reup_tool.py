"""
🎬 Tool Reup Pro - Full Features
Tính năng: Tách sub | Dịch | Đa giọng nói | Chỉnh âm thanh | Phụ đề | Logo | Text chạy
Version: 5.0
"""

import os
import sys
import json
import time
import shutil
import subprocess
import re
import threading
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime
from tkinter import filedialog, messagebox, colorchooser

import customtkinter as ctk
import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ========== CẤU HÌNH ==========
CONFIG_FILE = 'config.json'

# ========== DANH SÁCH GIỌNG NÓI ==========
# (Giữ nguyên như phiên bản trước)
PIPER_VOICES = {
    'Ngọc Huyền (Nữ - Truyền cảm)': {
        'model': 'ngochuyen.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'female',
        'desc': 'Giọng nữ truyền cảm, phù hợp kể chuyện'
    },
    'Ngọc Huyền Mới (Nữ - Sách nói)': {
        'model': 'ngochuyennew.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'female',
        'desc': 'Giọng nữ chuyên nghiệp, sách nói'
    },
    'Mai Phương (Nữ - Thuyết minh)': {
        'model': 'maiphuong.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'female',
        'desc': 'Giọng nữ thuyết minh phim'
    },
    'Mạnh Dũng (Nam - Trầm ấm)': {
        'model': 'manhdung.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'male',
        'desc': 'Giọng nam trầm ấm, tin tức'
    },
    'Minh Khang (Nam - Kịch tính)': {
        'model': 'minhkhang.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'male',
        'desc': 'Giọng nam kịch tính, hành động'
    },
    'Phương Trang (Nữ - Nhẹ nhàng)': {
        'model': 'phuongtrang.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'female',
        'desc': 'Giọng nữ nhẹ nhàng, tình cảm'
    },
    'Hoài Mỹ (Nữ - Tự nhiên)': {
        'model': 'hoaimy.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'female',
        'desc': 'Giọng nữ tự nhiên, gần gũi'
    },
    'Nam Minh (Nam - Rõ ràng)': {
        'model': 'namminh.onnx', 'engine': 'piper', 'lang': 'vi', 'gender': 'male',
        'desc': 'Giọng nam rõ ràng, tin tức'
    }
}

EDGE_VOICES = {
    'Nam Minh (Nam - Edge)': {'code': 'vi-VN-NamMinhNeural', 'engine': 'edge', 'lang': 'vi', 'gender': 'male', 'desc': 'Giọng nam rõ ràng (Edge)'},
    'Hoài Mỹ (Nữ - Edge)': {'code': 'vi-VN-HoaiMyNeural', 'engine': 'edge', 'lang': 'vi', 'gender': 'female', 'desc': 'Giọng nữ tự nhiên (Edge)'},
    'Andrew (Nam - Mỹ)': {'code': 'en-US-AndrewNeural', 'engine': 'edge', 'lang': 'en', 'gender': 'male', 'desc': 'Giọng nam Mỹ'},
    'Emma (Nữ - Mỹ)': {'code': 'en-US-EmmaNeural', 'engine': 'edge', 'lang': 'en', 'gender': 'female', 'desc': 'Giọng nữ Mỹ'},
    'Brian (Nam - Anh)': {'code': 'en-GB-BrianNeural', 'engine': 'edge', 'lang': 'en', 'gender': 'male', 'desc': 'Giọng nam Anh'},
    'Sonia (Nữ - Anh)': {'code': 'en-GB-SoniaNeural', 'engine': 'edge', 'lang': 'en', 'gender': 'female', 'desc': 'Giọng nữ Anh'},
    'Xiaoxiao (Nữ - Trung)': {'code': 'zh-CN-XiaoxiaoNeural', 'engine': 'edge', 'lang': 'zh', 'gender': 'female', 'desc': 'Giọng nữ Trung Quốc'},
    'Nanami (Nữ - Nhật)': {'code': 'ja-JP-NanamiNeural', 'engine': 'edge', 'lang': 'ja', 'gender': 'female', 'desc': 'Giọng nữ Nhật Bản'},
    'Sun-Hi (Nữ - Hàn)': {'code': 'ko-KR-SunHiNeural', 'engine': 'edge', 'lang': 'ko', 'gender': 'female', 'desc': 'Giọng nữ Hàn Quốc'},
    'Denise (Nữ - Pháp)': {'code': 'fr-FR-DeniseNeural', 'engine': 'edge', 'lang': 'fr', 'gender': 'female', 'desc': 'Giọng nữ Pháp'},
    'Katja (Nữ - Đức)': {'code': 'de-DE-KatjaNeural', 'engine': 'edge', 'lang': 'de', 'gender': 'female', 'desc': 'Giọng nữ Đức'},
    'Elvira (Nữ - TBN)': {'code': 'es-ES-ElviraNeural', 'engine': 'edge', 'lang': 'es', 'gender': 'female', 'desc': 'Giọng nữ Tây Ban Nha'}
}

TIKTOK_VOICES = {
    'Cô Gái Hoạt Ngôn (Nữ)': {'code': 'tiktok:Cô Gái Hoạt Ngôn (Nữ)', 'engine': 'tiktok', 'lang': 'vi', 'gender': 'female', 'desc': 'Giọng nữ hoạt ngôn'},
    'Thanh Niên Tự Tin (Nam)': {'code': 'tiktok:Thanh Niên Tự Tin (Nam)', 'engine': 'tiktok', 'lang': 'vi', 'gender': 'male', 'desc': 'Giọng nam tự tin'},
    'Nhỏ Ngọt Ngào (Nữ)': {'code': 'tiktok:Nhỏ Ngọt Ngào (Nữ)', 'engine': 'tiktok', 'lang': 'vi', 'gender': 'female', 'desc': 'Giọng nữ ngọt ngào'},
    'Mai (Nữ)': {'code': 'tiktok:Mai (Nữ)', 'engine': 'tiktok', 'lang': 'vi', 'gender': 'female', 'desc': 'Giọng nữ Mai'}
}

ALL_VOICES = {**PIPER_VOICES, **EDGE_VOICES, **TIKTOK_VOICES}

# ========== CLASS CHÍNH ==========
class ReupToolPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Cấu hình
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title("🎬 Tool Reup Pro - Full Features")
        self.geometry("1400x850")
        self.minsize(1200, 750)
        
        # Biến
        self.config = self.load_config()
        self.video_path = ""
        self.srt_path = ""
        self.translated_srt_path = ""
        self.audio_path = ""
        self.output_path = ""
        self.logo_path = ""
        self.is_processing = False
        self.cancel_event = threading.Event()
        
        # Biến cài đặt
        self.subtitle_settings = {
            'font': 'Arial',
            'font_size': 24,
            'color': '#FFFFFF',
            'outline_color': '#000000',
            'outline_width': 2,
            'shadow_color': '#000000',
            'shadow_offset': 2,
            'bg_color': '#00000080',
            'position': 'bottom',  # bottom, top, center
            'margin': 30
        }
        
        self.logo_settings = {
            'position': 'top-right',
            'size': 120,
            'opacity': 100,
            'margin_x': 20,
            'margin_y': 20
        }
        
        self.text_settings = {
            'rolling_text': '',
            'rolling_speed': 50,
            'rolling_direction': 'left',
            'fixed_text': '',
            'fixed_position': 'bottom-right',
            'text_color': '#FFFFFF',
            'text_size': 30,
            'text_font': 'Arial',
            'text_opacity': 100
        }
        
        self.audio_settings = {
            'volume': 100,
            'bass': 0,
            'treble': 0,
            'fade_in': 0,
            'fade_out': 0,
            'noise_reduction': False
        }
        
        # Xây dựng UI
        self.build_ui()
        self.load_saved_config()
        self.check_piper_installation()
    
    def load_config(self):
        """Load cấu hình"""
        default_config = {
            'piper_path': './piper/piper.exe',
            'model_path': './piper_models',
            'output_dir': './output',
            'temp_dir': './temp',
            'tiktok_session_id': '',
            'default_engine': 'piper',
            'default_voice': 'Ngọc Huyền (Nữ - Truyền cảm)',
            'subtitle_settings': self.subtitle_settings,
            'logo_settings': self.logo_settings,
            'text_settings': self.text_settings,
            'audio_settings': self.audio_settings
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Lưu cấu hình"""
        try:
            self.config['subtitle_settings'] = self.subtitle_settings
            self.config['logo_settings'] = self.logo_settings
            self.config['text_settings'] = self.text_settings
            self.config['audio_settings'] = self.audio_settings
            
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"Lỗi lưu config: {e}", "ERROR")
    
    def load_saved_config(self):
        """Load giá trị đã lưu"""
        # Output dir
        self.output_dir_var.set(self.config.get('output_dir', './output'))
        
        # Voice
        voice = self.config.get('default_voice', 'Ngọc Huyền (Nữ - Truyền cảm)')
        if voice in ALL_VOICES:
            self.voice_var.set(voice)
        
        # Engine
        engine = self.config.get('default_engine', 'piper')
        self.engine_var.set(engine)
        
        # TikTok session
        session = self.config.get('tiktok_session_id', '')
        if session:
            self.tiktok_session_var.set(session[:15] + '...')
            self.tiktok_session = session
        
        # Load settings
        self.subtitle_settings.update(self.config.get('subtitle_settings', {}))
        self.logo_settings.update(self.config.get('logo_settings', {}))
        self.text_settings.update(self.config.get('text_settings', {}))
        self.audio_settings.update(self.config.get('audio_settings', {}))
    
    # ========== UI ==========
    def build_ui(self):
        """Xây dựng giao diện"""
        
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🎬 Tool Reup Pro - Full Features",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="center")
        
        ctk.CTkLabel(
            header_frame,
            text="Tách sub | Dịch | Đa giọng nói | Chỉnh âm thanh | Phụ đề | Logo | Text chạy",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="center")
        
        # === TAB VIEW ===
        self.tabview = ctk.CTkTabview(main_frame, height=620)
        self.tabview.pack(fill="both", expand=True, pady=(10, 0))
        
        # Tab 1: Tách sub
        self.tab1 = self.tabview.add("🎤 Tách Sub")
        self.build_tab1()
        
        # Tab 2: Dịch
        self.tab2 = self.tabview.add("🌍 Dịch Sub")
        self.build_tab2()
        
        # Tab 3: Giọng nói
        self.tab3 = self.tabview.add("🎙️ Giọng Nói")
        self.build_tab3()
        
        # Tab 4: Âm thanh
        self.tab4 = self.tabview.add("🔊 Âm Thanh")
        self.build_tab4()
        
        # Tab 5: Phụ đề
        self.tab5 = self.tabview.add("📝 Phụ Đề")
        self.build_tab5()
        
        # Tab 6: Logo & Text
        self.tab6 = self.tabview.add("🎨 Logo & Text")
        self.build_tab6()
        
        # Tab 7: Ghép video
        self.tab7 = self.tabview.add("🎬 Ghép Video")
        self.build_tab7()
        
        # Tab 8: Log
        self.tab8 = self.tabview.add("📋 Log")
        self.build_tab8()
        
        # Status bar
        self.build_status_bar(main_frame)
    
    def build_status_bar(self, parent):
        """Xây dựng thanh trạng thái"""
        status_frame = ctk.CTkFrame(parent, height=35)
        status_frame.pack(fill="x", pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 Sẵn sàng",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=300, height=15)
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)
        
        self.piper_status_label = ctk.CTkLabel(
            status_frame,
            text="⏳ Đang kiểm tra Piper...",
            font=ctk.CTkFont(size=11)
        )
        self.piper_status_label.pack(side="right", padx=10)
    
    # ========== TAB 1: TÁCH SUB ==========
    def build_tab1(self):
        """Xây dựng tab tách phụ đề"""
        frame = ctk.CTkFrame(self.tab1)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Chọn video
        ctk.CTkLabel(
            frame,
            text="📁 Chọn video nguồn:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        video_row = ctk.CTkFrame(frame, fg_color="transparent")
        video_row.pack(fill="x", pady=(0, 15))
        
        self.video_label = ctk.CTkLabel(
            video_row,
            text="Chưa chọn video",
            fg_color="#2b2b2b",
            corner_radius=8,
            height=35
        )
        self.video_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            video_row,
            text="📂 Chọn Video",
            command=self.select_video,
            width=120
        ).pack(side="right")
        
        # Cài đặt
        setting_frame = ctk.CTkFrame(frame)
        setting_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            setting_frame,
            text="⚙️ Cài đặt:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Model và ngôn ngữ
        row1 = ctk.CTkFrame(setting_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(row1, text="Model:", width=80).pack(side="left")
        self.model_var = ctk.StringVar(value="base")
        ctk.CTkOptionMenu(
            row1,
            variable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            width=120
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(row1, text="Ngôn ngữ:", width=80).pack(side="left")
        self.extract_lang_var = ctk.StringVar(value="auto")
        ctk.CTkOptionMenu(
            row1,
            variable=self.extract_lang_var,
            values=["auto", "vi", "en", "zh", "ja", "ko", "fr", "es", "de"],
            width=120
        ).pack(side="left")
        
        # Nút
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.extract_btn = ctk.CTkButton(
            btn_frame,
            text="🎤 Bắt Đầu Tách Sub",
            command=self.start_extract_subtitle,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        self.extract_btn.pack(side="left", padx=(0, 10))
        
        self.extract_cancel_btn = ctk.CTkButton(
            btn_frame,
            text="⛔ Hủy",
            command=self.cancel_extract,
            height=40,
            fg_color="#c62828",
            hover_color="#b71c1c",
            state="disabled"
        )
        self.extract_cancel_btn.pack(side="left")
        
        # Thông tin
        self.srt_info_label = ctk.CTkLabel(
            frame,
            text="📝 Phụ đề sẽ được tạo sau khi tách",
            font=ctk.CTkFont(size=12)
        )
        self.srt_info_label.pack(anchor="w", pady=10)
    
    # ========== TAB 2: DỊCH ==========
    def build_tab2(self):
        """Xây dựng tab dịch phụ đề"""
        frame = ctk.CTkFrame(self.tab2)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Chọn SRT
        ctk.CTkLabel(
            frame,
            text="📝 Chọn file phụ đề (.srt):",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        srt_row = ctk.CTkFrame(frame, fg_color="transparent")
        srt_row.pack(fill="x", pady=(0, 15))
        
        self.srt_label = ctk.CTkLabel(
            srt_row,
            text="Chưa chọn file SRT",
            fg_color="#2b2b2b",
            corner_radius=8,
            height=35
        )
        self.srt_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            srt_row,
            text="📂 Chọn SRT",
            command=self.select_srt,
            width=120
        ).pack(side="right")
        
        # Cài đặt dịch
        setting_frame = ctk.CTkFrame(frame)
        setting_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            setting_frame,
            text="🌍 Cài đặt dịch:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        lang_row = ctk.CTkFrame(setting_frame, fg_color="transparent")
        lang_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(lang_row, text="Từ:", width=80).pack(side="left")
        self.source_lang_var = ctk.StringVar(value="auto")
        ctk.CTkOptionMenu(
            lang_row,
            variable=self.source_lang_var,
            values=["auto", "vi", "en", "zh", "ja", "ko", "fr", "es", "de"],
            width=120
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(lang_row, text="Sang:", width=80).pack(side="left")
        self.target_lang_var = ctk.StringVar(value="vi")
        ctk.CTkOptionMenu(
            lang_row,
            variable=self.target_lang_var,
            values=["vi", "en", "zh", "ja", "ko", "fr", "es", "de"],
            width=120
        ).pack(side="left")
        
        # Nút
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.translate_btn = ctk.CTkButton(
            btn_frame,
            text="🌍 Bắt Đầu Dịch",
            command=self.start_translate_subtitle,
            height=40,
            fg_color="#1565c0",
            hover_color="#0d47a1"
        )
        self.translate_btn.pack(side="left", padx=(0, 10))
        
        self.translate_info_label = ctk.CTkLabel(
            frame,
            text="📝 Phụ đề đã dịch sẽ được lưu với hậu tố '_translated'",
            font=ctk.CTkFont(size=12)
        )
        self.translate_info_label.pack(anchor="w", pady=10)
    
    # ========== TAB 3: GIỌNG NÓI ==========
    def build_tab3(self):
        """Xây dựng tab giọng nói"""
        frame = ctk.CTkScrollableFrame(self.tab3)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Chọn Engine
        engine_frame = ctk.CTkFrame(frame)
        engine_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            engine_frame,
            text="🎙️ Chọn Engine:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        engine_row = ctk.CTkFrame(engine_frame, fg_color="transparent")
        engine_row.pack(fill="x")
        
        self.engine_var = ctk.StringVar(value="piper")
        engines = [
            ("Piper TTS (Offline)", "piper"),
            ("Edge TTS (Online)", "edge"),
            ("TikTok TTS", "tiktok")
        ]
        
        for text, value in engines:
            radio = ctk.CTkRadioButton(
                engine_row,
                text=text,
                variable=self.engine_var,
                value=value,
                command=self.update_voice_list
            )
            radio.pack(side="left", padx=(0, 20))
        
        # Chọn giọng
        voice_frame = ctk.CTkFrame(frame)
        voice_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            voice_frame,
            text="🗣️ Chọn giọng nói:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        voice_row = ctk.CTkFrame(voice_frame, fg_color="transparent")
        voice_row.pack(fill="x")
        
        self.voice_var = ctk.StringVar(value="Ngọc Huyền (Nữ - Truyền cảm)")
        self.voice_menu = ctk.CTkOptionMenu(
            voice_row,
            variable=self.voice_var,
            values=list(PIPER_VOICES.keys()),
            width=350
        )
        self.voice_menu.pack(side="left", padx=(0, 20))
        
        # Thông tin giọng
        self.voice_info_label = ctk.CTkLabel(
            voice_row,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888"
        )
        self.voice_info_label.pack(side="left")
        
        # Cài đặt giọng
        settings_frame = ctk.CTkFrame(frame)
        settings_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            settings_frame,
            text="⚙️ Cài đặt giọng:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Speed
        speed_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        speed_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(speed_row, text="Tốc độ:", width=80).pack(side="left")
        self.speed_slider = ctk.CTkSlider(
            speed_row,
            from_=0.5,
            to=2.0,
            number_of_steps=15,
            command=self.update_speed_label
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.speed_slider.set(1.0)
        
        self.speed_label = ctk.CTkLabel(speed_row, text="1.0x", width=50)
        self.speed_label.pack(side="left")
        
        # TikTok Session
        tiktok_frame = ctk.CTkFrame(frame)
        tiktok_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            tiktok_frame,
            text="🔐 TikTok Session ID (cho TikTok TTS):",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        tiktok_row = ctk.CTkFrame(tiktok_frame, fg_color="transparent")
        tiktok_row.pack(fill="x")
        
        self.tiktok_session_var = ctk.StringVar()
        self.tiktok_session_entry = ctk.CTkEntry(
            tiktok_row,
            textvariable=self.tiktok_session_var,
            placeholder_text="Nhập sessionid hoặc cookie TikTok",
            width=400
        )
        self.tiktok_session_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            tiktok_row,
            text="📋 Dán từ Clipboard",
            command=self.paste_tiktok_session,
            width=150
        ).pack(side="left")
        
        # Nút tạo giọng
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.tts_btn = ctk.CTkButton(
            btn_frame,
            text="🎙️ Tạo Giọng Từ Sub",
            command=self.start_generate_voice,
            height=40,
            fg_color="#e65100",
            hover_color="#bf360c"
        )
        self.tts_btn.pack(side="left", padx=(0, 10))
        
        self.tts_cancel_btn = ctk.CTkButton(
            btn_frame,
            text="⛔ Hủy",
            command=self.cancel_tts,
            height=40,
            fg_color="#c62828",
            hover_color="#b71c1c",
            state="disabled"
        )
        self.tts_cancel_btn.pack(side="left")
        
        self.audio_info_label = ctk.CTkLabel(
            frame,
            text="🎵 File audio sẽ được tạo sau khi tạo giọng",
            font=ctk.CTkFont(size=12)
        )
        self.audio_info_label.pack(anchor="w", pady=10)
    
    # ========== TAB 4: ÂM THANH ==========
    def build_tab4(self):
        """Xây dựng tab chỉnh âm thanh"""
        frame = ctk.CTkScrollableFrame(self.tab4)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            frame,
            text="🔊 Chỉnh âm thanh",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Volume
        vol_frame = ctk.CTkFrame(frame)
        vol_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(vol_frame, text="Âm lượng:", width=100).pack(side="left")
        self.volume_slider = ctk.CTkSlider(
            vol_frame,
            from_=0,
            to=200,
            number_of_steps=200
        )
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.volume_slider.set(100)
        
        self.volume_label = ctk.CTkLabel(vol_frame, text="100%", width=50)
        self.volume_label.pack(side="left")
        
        # Bass
        bass_frame = ctk.CTkFrame(frame)
        bass_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(bass_frame, text="Bass:", width=100).pack(side="left")
        self.bass_slider = ctk.CTkSlider(
            bass_frame,
            from_=-10,
            to=10,
            number_of_steps=20
        )
        self.bass_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.bass_slider.set(0)
        
        self.bass_label = ctk.CTkLabel(bass_frame, text="0", width=50)
        self.bass_label.pack(side="left")
        
        # Treble
        treble_frame = ctk.CTkFrame(frame)
        treble_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(treble_frame, text="Treble:", width=100).pack(side="left")
        self.treble_slider = ctk.CTkSlider(
            treble_frame,
            from_=-10,
            to=10,
            number_of_steps=20
        )
        self.treble_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.treble_slider.set(0)
        
        self.treble_label = ctk.CTkLabel(treble_frame, text="0", width=50)
        self.treble_label.pack(side="left")
        
        # Fade In/Out
        fade_frame = ctk.CTkFrame(frame)
        fade_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(fade_frame, text="Fade In (giây):", width=100).pack(side="left")
        self.fade_in_var = ctk.StringVar(value="0")
        ctk.CTkEntry(fade_frame, textvariable=self.fade_in_var, width=80).pack(side="left", padx=10)
        
        ctk.CTkLabel(fade_frame, text="Fade Out (giây):", width=100).pack(side="left", padx=(20, 0))
        self.fade_out_var = ctk.StringVar(value="0")
        ctk.CTkEntry(fade_frame, textvariable=self.fade_out_var, width=80).pack(side="left", padx=10)
        
        # Noise Reduction
        nr_frame = ctk.CTkFrame(frame)
        nr_frame.pack(fill="x", pady=(0, 10))
        
        self.noise_reduction_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            nr_frame,
            text="🔇 Giảm nhiễu (Noise Reduction)",
            variable=self.noise_reduction_var
        ).pack(anchor="w")
        
        # Thông tin
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Cài đặt âm thanh sẽ được áp dụng khi ghép video",
            font=ctk.CTkFont(size=12),
            text_color="#888"
        ).pack(anchor="w")
    
    # ========== TAB 5: PHỤ ĐỀ ==========
    def build_tab5(self):
        """Xây dựng tab cài đặt phụ đề"""
        frame = ctk.CTkScrollableFrame(self.tab5)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            frame,
            text="📝 Cài đặt phụ đề",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Font
        font_frame = ctk.CTkFrame(frame)
        font_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(font_frame, text="Font:", width=100).pack(side="left")
        self.font_var = ctk.StringVar(value="Arial")
        ctk.CTkOptionMenu(
            font_frame,
            variable=self.font_var,
            values=["Arial", "Times New Roman", "Verdana", "Tahoma", "Segoe UI", "Roboto"],
            width=150
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(font_frame, text="Size:", width=60).pack(side="left")
        self.font_size_var = ctk.StringVar(value="24")
        ctk.CTkEntry(font_frame, textvariable=self.font_size_var, width=60).pack(side="left", padx=10)
        
        # Màu sắc
        color_frame = ctk.CTkFrame(frame)
        color_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(color_frame, text="Màu chữ:", width=100).pack(side="left")
        self.color_preview = ctk.CTkButton(
            color_frame,
            text="",
            width=40,
            height=30,
            fg_color="#FFFFFF",
            command=self.choose_text_color
        )
        self.color_preview.pack(side="left", padx=10)
        
        ctk.CTkLabel(color_frame, text="Màu viền:", width=100).pack(side="left", padx=(20, 0))
        self.outline_color_preview = ctk.CTkButton(
            color_frame,
            text="",
            width=40,
            height=30,
            fg_color="#000000",
            command=self.choose_outline_color
        )
        self.outline_color_preview.pack(side="left", padx=10)
        
        # Độ dày viền
        outline_frame = ctk.CTkFrame(frame)
        outline_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(outline_frame, text="Độ dày viền:", width=100).pack(side="left")
        self.outline_width_var = ctk.StringVar(value="2")
        ctk.CTkEntry(outline_frame, textvariable=self.outline_width_var, width=60).pack(side="left", padx=10)
        
        ctk.CTkLabel(outline_frame, text="Đổ bóng:", width=100).pack(side="left", padx=(20, 0))
        self.shadow_offset_var = ctk.StringVar(value="2")
        ctk.CTkEntry(outline_frame, textvariable=self.shadow_offset_var, width=60).pack(side="left", padx=10)
        
        # Vị trí
        pos_frame = ctk.CTkFrame(frame)
        pos_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(pos_frame, text="Vị trí:", width=100).pack(side="left")
        self.position_var = ctk.StringVar(value="bottom")
        ctk.CTkOptionMenu(
            pos_frame,
            variable=self.position_var,
            values=["bottom", "top", "center"],
            width=120
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(pos_frame, text="Lề (px):", width=100).pack(side="left", padx=(20, 0))
        self.margin_var = ctk.StringVar(value="30")
        ctk.CTkEntry(pos_frame, textvariable=self.margin_var, width=60).pack(side="left", padx=10)
        
        # Nền
        bg_frame = ctk.CTkFrame(frame)
        bg_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(bg_frame, text="Màu nền:", width=100).pack(side="left")
        self.bg_color_preview = ctk.CTkButton(
            bg_frame,
            text="",
            width=40,
            height=30,
            fg_color="#00000080",
            command=self.choose_bg_color
        )
        self.bg_color_preview.pack(side="left", padx=10)
        
        ctk.CTkLabel(bg_frame, text="Độ mờ:", width=100).pack(side="left", padx=(20, 0))
        self.bg_opacity_var = ctk.StringVar(value="50")
        ctk.CTkEntry(bg_frame, textvariable=self.bg_opacity_var, width=60).pack(side="left", padx=10)
    
    # ========== TAB 6: LOGO & TEXT ==========
    def build_tab6(self):
        """Xây dựng tab logo và text"""
        frame = ctk.CTkScrollableFrame(self.tab6)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === LOGO ===
        ctk.CTkLabel(
            frame,
            text="🎨 Logo",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Chọn logo
        logo_row = ctk.CTkFrame(frame, fg_color="transparent")
        logo_row.pack(fill="x", pady=(0, 10))
        
        self.logo_label = ctk.CTkLabel(
            logo_row,
            text="Chưa chọn logo",
            fg_color="#2b2b2b",
            corner_radius=8,
            height=35
        )
        self.logo_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            logo_row,
            text="📂 Chọn Logo",
            command=self.select_logo,
            width=120
        ).pack(side="right", padx=(0, 5))
        
        ctk.CTkButton(
            logo_row,
            text="🗑️ Xóa",
            command=self.clear_logo,
            width=80
        ).pack(side="right")
        
        # Cài đặt logo
        logo_settings_frame = ctk.CTkFrame(frame)
        logo_settings_frame.pack(fill="x", pady=(0, 10))
        
        # Vị trí
        pos_row = ctk.CTkFrame(logo_settings_frame, fg_color="transparent")
        pos_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(pos_row, text="Vị trí:", width=80).pack(side="left")
        self.logo_pos_var = ctk.StringVar(value="top-right")
        ctk.CTkOptionMenu(
            pos_row,
            variable=self.logo_pos_var,
            values=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
            width=150
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(pos_row, text="Kích thước:", width=80).pack(side="left", padx=(20, 0))
        self.logo_size_var = ctk.StringVar(value="120")
        ctk.CTkEntry(pos_row, textvariable=self.logo_size_var, width=60).pack(side="left", padx=10)
        
        # Độ trong suốt
        opacity_row = ctk.CTkFrame(logo_settings_frame, fg_color="transparent")
        opacity_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(opacity_row, text="Độ trong suốt:", width=80).pack(side="left")
        self.logo_opacity_slider = ctk.CTkSlider(
            opacity_row,
            from_=10,
            to=100,
            number_of_steps=90
        )
        self.logo_opacity_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.logo_opacity_slider.set(100)
        
        self.logo_opacity_label = ctk.CTkLabel(opacity_row, text="100%", width=50)
        self.logo_opacity_label.pack(side="left")
        
        # === TEXT CHẠY ===
        ctk.CTkLabel(
            frame,
            text="📝 Text Chạy (Rolling Text)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 10))
        
        # Nội dung
        rolling_row = ctk.CTkFrame(frame, fg_color="transparent")
        rolling_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(rolling_row, text="Nội dung:", width=80).pack(side="left")
        self.rolling_text_var = ctk.StringVar(value="")
        ctk.CTkEntry(
            rolling_row,
            textvariable=self.rolling_text_var,
            placeholder_text="Nhập text chạy...",
            width=400
        ).pack(side="left", fill="x", expand=True, padx=10)
        
        # Cài đặt text chạy
        rolling_settings = ctk.CTkFrame(frame, fg_color="transparent")
        rolling_settings.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(rolling_settings, text="Tốc độ:", width=80).pack(side="left")
        self.rolling_speed_slider = ctk.CTkSlider(
            rolling_settings,
            from_=10,
            to=100,
            number_of_steps=90
        )
        self.rolling_speed_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.rolling_speed_slider.set(50)
        
        self.rolling_speed_label = ctk.CTkLabel(rolling_settings, text="50", width=50)
        self.rolling_speed_label.pack(side="left")
        
        ctk.CTkLabel(rolling_settings, text="Hướng:", width=80).pack(side="left", padx=(20, 0))
        self.rolling_dir_var = ctk.StringVar(value="left")
        ctk.CTkOptionMenu(
            rolling_settings,
            variable=self.rolling_dir_var,
            values=["left", "right", "up", "down"],
            width=100
        ).pack(side="left", padx=10)
        
        # === TEXT CỐ ĐỊNH ===
        ctk.CTkLabel(
            frame,
            text="📌 Text Cố Định",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 10))
        
        # Nội dung
        fixed_row = ctk.CTkFrame(frame, fg_color="transparent")
        fixed_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(fixed_row, text="Nội dung:", width=80).pack(side="left")
        self.fixed_text_var = ctk.StringVar(value="")
        ctk.CTkEntry(
            fixed_row,
            textvariable=self.fixed_text_var,
            placeholder_text="Nhập text cố định...",
            width=400
        ).pack(side="left", fill="x", expand=True, padx=10)
        
        # Cài đặt text cố định
        fixed_settings = ctk.CTkFrame(frame, fg_color="transparent")
        fixed_settings.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(fixed_settings, text="Vị trí:", width=80).pack(side="left")
        self.fixed_pos_var = ctk.StringVar(value="bottom-right")
        ctk.CTkOptionMenu(
            fixed_settings,
            variable=self.fixed_pos_var,
            values=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
            width=150
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(fixed_settings, text="Kích thước:", width=80).pack(side="left", padx=(20, 0))
        self.fixed_size_var = ctk.StringVar(value="30")
        ctk.CTkEntry(fixed_settings, textvariable=self.fixed_size_var, width=60).pack(side="left", padx=10)
        
        ctk.CTkLabel(fixed_settings, text="Độ mờ:", width=80).pack(side="left", padx=(20, 0))
        self.fixed_opacity_var = ctk.StringVar(value="100")
        ctk.CTkEntry(fixed_settings, textvariable=self.fixed_opacity_var, width=60).pack(side="left", padx=10)
    
    # ========== TAB 7: GHÉP VIDEO ==========
    def build_tab7(self):
        """Xây dựng tab ghép video"""
        frame = ctk.CTkScrollableFrame(self.tab7)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Thông tin
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            info_frame,
            text="📋 Các file sẽ được ghép:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.video_file_label = ctk.CTkLabel(info_frame, text="🎬 Video: Chưa chọn")
        self.video_file_label.pack(anchor="w")
        
        self.srt_file_label = ctk.CTkLabel(info_frame, text="📝 Phụ đề: Chưa chọn")
        self.srt_file_label.pack(anchor="w")
        
        self.audio_file_label = ctk.CTkLabel(info_frame, text="🎵 Audio: Chưa tạo")
        self.audio_file_label.pack(anchor="w")
        
        self.logo_file_label = ctk.CTkLabel(info_frame, text="🎨 Logo: Chưa chọn")
        self.logo_file_label.pack(anchor="w")
        
        # Output
        output_frame = ctk.CTkFrame(frame)
        output_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            output_frame,
            text="📁 Thư mục output:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        output_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_row.pack(fill="x")
        
        self.output_dir_var = ctk.StringVar(value="./output")
        self.output_entry = ctk.CTkEntry(
            output_row,
            textvariable=self.output_dir_var,
            width=400
        )
        self.output_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            output_row,
            text="📂 Chọn",
            command=self.select_output_dir,
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            output_row,
            text="📂 Mở",
            command=self.open_output_dir,
            width=100
        ).pack(side="left")
        
        # Nút
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        self.render_btn = ctk.CTkButton(
            btn_frame,
            text="🎬 Bắt Đầu Ghép Video",
            command=self.start_render,
            height=45,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        self.render_btn.pack(side="left", padx=(0, 10))
        
        self.render_cancel_btn = ctk.CTkButton(
            btn_frame,
            text="⛔ Hủy",
            command=self.cancel_render,
            height=45,
            fg_color="#c62828",
            hover_color="#b71c1c",
            state="disabled"
        )
        self.render_cancel_btn.pack(side="left")
        
        # Thông tin
        self.render_info_label = ctk.CTkLabel(
            frame,
            text="🔄 Chọn đủ video, phụ đề và audio để bắt đầu ghép",
            font=ctk.CTkFont(size=12)
        )
        self.render_info_label.pack(anchor="w", pady=10)
    
    # ========== TAB 8: LOG ==========
    def build_tab8(self):
        """Xây dựng tab log"""
        frame = ctk.CTkFrame(self.tab8)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        log_header = ctk.CTkFrame(frame, fg_color="transparent")
        log_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            log_header,
            text="📋 Nhật ký tiến trình:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            log_header,
            text="🗑️ Xóa Log",
            command=self.clear_log,
            width=100
        ).pack(side="right")
        
        self.log_text = ctk.CTkTextbox(frame, font=ctk.CTkFont(size=12))
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")
    
    # ========== HÀM XỬ LÝ ==========
    
    def log(self, message, level="INFO"):
        """Ghi log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"INFO": "🟢", "WARNING": "🟡", "ERROR": "🔴", "SUCCESS": "✅", "PROGRESS": "⏳"}
        prefix = colors.get(level, "📌")
        log_line = f"[{timestamp}] {prefix} {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_line)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        
        self.update_idletasks()
        print(log_line.strip())
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
    
    def update_status(self, text, color="white"):
        """Cập nhật status"""
        self.status_label.configure(text=text, text_color=color)
    
    def update_progress(self, value):
        """Cập nhật progress"""
        self.progress_bar.set(value)
    
    def check_piper_installation(self):
        """Kiểm tra Piper đã cài đặt chưa"""
        piper_path = self.config.get('piper_path', './piper/piper.exe')
        if os.path.exists(piper_path):
            self.piper_status_label.configure(text="✅ Piper đã sẵn sàng", text_color="green")
            self.log("✅ Piper TTS đã sẵn sàng", "SUCCESS")
        else:
            self.piper_status_label.configure(text="❌ Chưa cài Piper", text_color="red")
            self.log("⚠️ Piper TTS chưa được cài đặt", "WARNING")
    
    # ========== CÁC HÀM CHỌN MÀU ==========
    
    def choose_text_color(self):
        """Chọn màu chữ"""
        color = colorchooser.askcolor(initialcolor=self.subtitle_settings['color'])[1]
        if color:
            self.subtitle_settings['color'] = color
            self.color_preview.configure(fg_color=color)
            self.save_config()
    
    def choose_outline_color(self):
        """Chọn màu viền"""
        color = colorchooser.askcolor(initialcolor=self.subtitle_settings['outline_color'])[1]
        if color:
            self.subtitle_settings['outline_color'] = color
            self.outline_color_preview.configure(fg_color=color)
            self.save_config()
    
    def choose_bg_color(self):
        """Chọn màu nền"""
        color = colorchooser.askcolor(initialcolor="#000000")[1]
        if color:
            self.bg_color_preview.configure(fg_color=color + "80")
            self.save_config()
    
    def select_logo(self):
        """Chọn logo"""
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
        path = filedialog.askopenfilename(title="Chọn logo", filetypes=filetypes)
        if path:
            self.logo_path = path
            self.logo_label.configure(text=os.path.basename(path))
            self.logo_file_label.configure(text=f"🎨 Logo: {os.path.basename(path)}")
            self.log(f"✅ Đã chọn logo: {os.path.basename(path)}", "SUCCESS")
    
    def clear_logo(self):
        """Xóa logo"""
        self.logo_path = ""
        self.logo_label.configure(text="Chưa chọn logo")
        self.logo_file_label.configure(text="🎨 Logo: Chưa chọn")
        self.log("🗑️ Đã xóa logo", "INFO")
    
    # ========== HÀM SELECT ==========
    
    def select_video(self):
        """Chọn video"""
        filetypes = [("Video files", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm")]
        path = filedialog.askopenfilename(title="Chọn video", filetypes=filetypes)
        if path:
            self.video_path = path
            self.video_label.configure(text=os.path.basename(path))
            self.video_file_label.configure(text=f"🎬 Video: {os.path.basename(path)}")
            self.log(f"✅ Đã chọn video: {os.path.basename(path)}", "SUCCESS")
            
            srt_path = os.path.splitext(path)[0] + '.srt'
            if os.path.exists(srt_path):
                self.srt_path = srt_path
                self.srt_label.configure(text=os.path.basename(srt_path))
                self.srt_file_label.configure(text=f"📝 Phụ đề: {os.path.basename(srt_path)}")
                self.log(f"✅ Tự động tìm thấy phụ đề: {os.path.basename(srt_path)}", "SUCCESS")
    
    def select_srt(self):
        """Chọn file SRT"""
        filetypes = [("SRT files", "*.srt")]
        path = filedialog.askopenfilename(title="Chọn file SRT", filetypes=filetypes)
        if path:
            self.srt_path = path
            self.srt_label.configure(text=os.path.basename(path))
            self.srt_file_label.configure(text=f"📝 Phụ đề: {os.path.basename(path)}")
            self.log(f"✅ Đã chọn SRT: {os.path.basename(path)}", "SUCCESS")
    
    def select_output_dir(self):
        """Chọn thư mục output"""
        path = filedialog.askdirectory(title="Chọn thư mục output")
        if path:
            self.output_dir_var.set(path)
            self.config['output_dir'] = path
            self.save_config()
            self.log(f"✅ Đã chọn output: {path}", "SUCCESS")
    
    def open_output_dir(self):
        """Mở thư mục output"""
        path = self.output_dir_var.get()
        if os.path.exists(path):
            os.startfile(path)
        else:
            os.makedirs(path, exist_ok=True)
            os.startfile(path)
    
    def paste_tiktok_session(self):
        """Dán TikTok session từ clipboard"""
        try:
            text = self.clipboard_get().strip()
            match = re.search(r'(?:^|[;\\s])sessionid=([^;\\s]+)', text, re.IGNORECASE)
            if match:
                session = match.group(1).strip()
            else:
                session = text
            
            if len(session) > 10:
                self.tiktok_session_var.set(session)
                self.config['tiktok_session_id'] = session
                self.save_config()
                self.log(f"✅ Đã dán TikTok Session: {session[:10]}...", "SUCCESS")
            else:
                self.log("⚠️ Không tìm thấy session ID hợp lệ", "WARNING")
        except:
            self.log("❌ Không đọc được clipboard", "ERROR")
    
    # ========== CÁC HÀM XỬ LÝ CHÍNH ==========
    
    # Tách sub (giữ nguyên từ phiên bản trước)
    def start_extract_subtitle(self):
        """Bắt đầu tách phụ đề"""
        if not self.video_path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn video!")
            return
        
        self.is_processing = True
        self.cancel_event.clear()
        self.extract_btn.configure(state="disabled", text="⏳ Đang tách...")
        self.extract_cancel_btn.configure(state="normal")
        self.update_status("⏳ Đang tách phụ đề...", "yellow")
        
        self.log("🎤 Bắt đầu tách phụ đề...", "PROGRESS")
        
        def extract_thread():
            try:
                from faster_whisper import WhisperModel
                
                model_size = self.model_var.get()
                language = self.extract_lang_var.get()
                language = None if language == "auto" else language
                
                self.log(f"⚙️ Model: {model_size}, Ngôn ngữ: {self.extract_lang_var.get()}", "INFO")
                
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                
                output_srt = os.path.splitext(self.video_path)[0] + '.srt'
                
                segments, info = model.transcribe(
                    self.video_path,
                    beam_size=5,
                    language=language,
                    vad_filter=True,
                    vad_parameters={"min_silence_duration_ms": 500}
                )
                
                count = 0
                with open(output_srt, 'w', encoding='utf-8') as f:
                    for segment in segments:
                        if self.cancel_event.is_set():
                            raise Exception("Đã hủy")
                        text = str(segment.text).strip()
                        if not text:
                            continue
                        count += 1
                        f.write(f"{count}\n{self.format_srt_time(segment.start)} --> {self.format_srt_time(segment.end)}\n{text}\n\n")
                        
                        if count % 10 == 0:
                            self.update_progress(min(0.9, count / 100))
                
                if count > 0:
                    self.srt_path = output_srt
                    self.srt_label.configure(text=os.path.basename(output_srt))
                    self.srt_file_label.configure(text=f"📝 Phụ đề: {os.path.basename(output_srt)}")
                    self.log(f"✅ Đã tách {count} đoạn phụ đề", "SUCCESS")
                    self.update_status("✅ Tách sub thành công", "green")
                    self.update_progress(1.0)
                    self.after(0, lambda: messagebox.showinfo(
                        "Thành công",
                        f"Đã tách {count} đoạn phụ đề!\nLưu tại: {output_srt}"
                    ))
                else:
                    self.log("❌ Không tìm thấy lời thoại", "ERROR")
                    self.update_status("❌ Không có lời thoại", "red")
                    
            except Exception as e:
                if "hủy" in str(e).lower():
                    self.log("⛔ Đã hủy tách sub", "WARNING")
                    self.update_status("⛔ Đã hủy", "orange")
                else:
                    self.log(f"❌ Lỗi tách sub: {e}", "ERROR")
                    self.update_status("❌ Lỗi", "red")
            
            finally:
                self.is_processing = False
                self.extract_btn.configure(state="normal", text="🎤 Bắt Đầu Tách Sub")
                self.extract_cancel_btn.configure(state="disabled")
        
        threading.Thread(target=extract_thread, daemon=True).start()
    
    def cancel_extract(self):
        """Hủy tách sub"""
        if self.is_processing:
            self.cancel_event.set()
            self.log("⛔ Đang hủy tách sub...", "WARNING")
            self.extract_cancel_btn.configure(state="disabled", text="⏳ Đang hủy...")
    
    # Dịch (giữ nguyên)
    def start_translate_subtitle(self):
        """Bắt đầu dịch phụ đề"""
        if not self.srt_path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file SRT!")
            return
        
        self.translate_btn.configure(state="disabled", text="⏳ Đang dịch...")
        self.update_status("⏳ Đang dịch phụ đề...", "yellow")
        self.update_progress(0)
        
        self.log(f"🌍 Bắt đầu dịch từ {self.source_lang_var.get()} sang {self.target_lang_var.get()}", "PROGRESS")
        
        def translate_thread():
            try:
                with open(self.srt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                blocks = self.parse_srt(content)
                
                if not blocks:
                    raise Exception("Không tìm thấy phụ đề hợp lệ")
                
                self.log(f"📝 Đã tìm thấy {len(blocks)} đoạn phụ đề", "INFO")
                
                translated_blocks = []
                for i, block in enumerate(blocks):
                    if self.cancel_event.is_set():
                        raise Exception("Đã hủy")
                    
                    progress = (i + 1) / len(blocks)
                    self.update_progress(progress)
                    
                    translated_text = self.translate_text(block['text'])
                    translated_blocks.append({
                        **block,
                        'text': translated_text
                    })
                    
                    if (i + 1) % 10 == 0:
                        self.log(f"📝 Đã dịch {i + 1}/{len(blocks)} đoạn", "INFO")
                
                output_path = os.path.splitext(self.srt_path)[0] + '_translated.srt'
                with open(output_path, 'w', encoding='utf-8') as f:
                    for block in translated_blocks:
                        f.write(f"{block['index']}\n")
                        f.write(f"{block['start']} --> {block['end']}\n")
                        f.write(f"{block['text']}\n\n")
                
                self.translated_srt_path = output_path
                self.log(f"✅ Đã dịch xong {len(translated_blocks)} đoạn", "SUCCESS")
                self.update_status("✅ Dịch thành công", "green")
                self.update_progress(1.0)
                
                self.after(0, lambda: messagebox.showinfo(
                    "Thành công",
                    f"Đã dịch {len(translated_blocks)} đoạn phụ đề!\nLưu tại: {output_path}"
                ))
                
            except Exception as e:
                if "hủy" in str(e).lower():
                    self.log("⛔ Đã hủy dịch", "WARNING")
                    self.update_status("⛔ Đã hủy", "orange")
                else:
                    self.log(f"❌ Lỗi dịch: {e}", "ERROR")
                    self.update_status("❌ Lỗi", "red")
            
            finally:
                self.translate_btn.configure(state="normal", text="🌍 Bắt Đầu Dịch")
        
        threading.Thread(target=translate_thread, daemon=True).start()
    
    def parse_srt(self, content):
        """Parse SRT"""
        pattern = re.compile(
            r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)',
            re.DOTALL
        )
        
        blocks = []
        for match in pattern.finditer(content):
            blocks.append({
                'index': int(match.group(1)),
                'start': match.group(2),
                'end': match.group(3),
                'text': match.group(4).strip()
            })
        
        return blocks
    
    def translate_text(self, text):
        """Dịch văn bản"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': self.source_lang_var.get(),
                'tl': self.target_lang_var.get(),
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                translated = ''.join([part[0] for part in data[0]])
                return translated
        except Exception as e:
            self.log(f"⚠️ Lỗi dịch: {e}", "WARNING")
        
        return text
    
    # Tạo giọng (giữ nguyên)
    def start_generate_voice(self):
        """Tạo giọng từ phụ đề"""
        srt_to_use = self.translated_srt_path or self.srt_path
        if not srt_to_use or not os.path.exists(srt_to_use):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc dịch phụ đề trước!")
            return
        
        if self.engine_var.get() == "tiktok":
            session = self.tiktok_session_var.get().strip()
            if not session:
                result = messagebox.askyesno(
                    "Thiếu Session",
                    "TikTok TTS cần Session ID. Muốn nhập ngay không?"
                )
                if result:
                    self.tabview.set("🎙️ Giọng Nói")
                    self.tiktok_session_entry.focus()
                return
            self.config['tiktok_session_id'] = session
            self.save_config()
        
        self.is_processing = True
        self.cancel_event.clear()
        self.tts_btn.configure(state="disabled", text="⏳ Đang tạo...")
        self.tts_cancel_btn.configure(state="normal")
        self.update_status("⏳ Đang tạo giọng...", "yellow")
        self.update_progress(0)
        
        self.log(f"🎙️ Bắt đầu tạo giọng với engine: {self.engine_var.get()}", "PROGRESS")
        
        def tts_thread():
            try:
                with open(srt_to_use, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                blocks = self.parse_srt(content)
                if not blocks:
                    raise Exception("Không có phụ đề")
                
                full_text = ' '.join([block['text'] for block in blocks])
                self.log(f"📝 Tạo giọng cho {len(full_text)} ký tự", "INFO")
                
                audio_path = os.path.splitext(srt_to_use)[0] + '_voice.mp3'
                
                engine = self.engine_var.get()
                voice = self.voice_var.get()
                speed = self.speed_slider.get()
                
                if engine == "piper":
                    self.generate_piper_voice(full_text, audio_path, voice, speed)
                elif engine == "edge":
                    self.generate_edge_voice(full_text, audio_path, voice, speed)
                elif engine == "tiktok":
                    self.generate_tiktok_voice(full_text, audio_path, voice, speed)
                else:
                    raise Exception(f"Engine {engine} không hỗ trợ")
                
                if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                    self.audio_path = audio_path
                    self.audio_file_label.configure(text=f"🎵 Audio: {os.path.basename(audio_path)}")
                    self.log(f"✅ Đã tạo giọng: {os.path.basename(audio_path)}", "SUCCESS")
                    self.update_status("✅ Tạo giọng thành công", "green")
                    self.update_progress(1.0)
                    
                    self.after(0, lambda: messagebox.showinfo(
                        "Thành công",
                        f"Đã tạo giọng thành công!\nLưu tại: {audio_path}"
                    ))
                else:
                    raise Exception("File audio rỗng hoặc lỗi")
                    
            except Exception as e:
                if "hủy" in str(e).lower():
                    self.log("⛔ Đã hủy tạo giọng", "WARNING")
                    self.update_status("⛔ Đã hủy", "orange")
                else:
                    self.log(f"❌ Lỗi tạo giọng: {e}", "ERROR")
                    self.update_status("❌ Lỗi", "red")
            
            finally:
                self.is_processing = False
                self.tts_btn.configure(state="normal", text="🎙️ Tạo Giọng Từ Sub")
                self.tts_cancel_btn.configure(state="disabled")
        
        threading.Thread(target=tts_thread, daemon=True).start()
    
    def generate_piper_voice(self, text, output_path, voice, speed):
        """Tạo giọng với Piper TTS"""
        piper_path = self.config.get('piper_path', './piper/piper.exe')
        model_path = self.config.get('model_path', './piper_models')
        
        if not os.path.exists(piper_path):
            raise Exception(f"Không tìm thấy Piper tại: {piper_path}")
        
        voice_info = PIPER_VOICES.get(voice, {})
        model_file = voice_info.get('model', 'ngochuyen.onnx')
        model_full_path = os.path.join(model_path, model_file)
        
        if not os.path.exists(model_full_path):
            raise Exception(f"Không tìm thấy model: {model_full_path}")
        
        length_scale = 1.0 / speed
        cmd = [
            piper_path,
            '--model', model_full_path,
            '--length_scale', str(length_scale),
            '--output_file', output_path,
            '--sentence_silence', '0.15'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        stdout, stderr = process.communicate(input=text)
        
        if process.returncode != 0:
            raise Exception(f"Piper lỗi: {stderr}")
    
    def generate_edge_voice(self, text, output_path, voice, speed):
        """Tạo giọng với Edge TTS"""
        import edge_tts
        
        voice_info = EDGE_VOICES.get(voice, {})
        voice_code = voice_info.get('code', 'vi-VN-NamMinhNeural')
        
        rate = int((speed - 1.0) * 100)
        rate_str = f"+{rate}%" if rate >= 0 else f"{rate}%"
        
        async def generate():
            communicate = edge_tts.Communicate(text, voice_code, rate=rate_str)
            await communicate.save(output_path)
        
        asyncio.run(generate())
    
    def generate_tiktok_voice(self, text, output_path, voice, speed):
        """Tạo giọng với TikTok TTS"""
        import edge_tts
        
        session = self.tiktok_session_var.get().strip()
        if not session:
            self.log("⚠️ TikTok TTS cần session, fallback sang Edge", "WARNING")
            voice_fallback = "vi-VN-NamMinhNeural"
            rate = int((speed - 1.0) * 100)
            rate_str = f"+{rate}%" if rate >= 0 else f"{rate}%"
            
            async def generate_fallback():
                communicate = edge_tts.Communicate(text, voice_fallback, rate=rate_str)
                await communicate.save(output_path)
            
            asyncio.run(generate_fallback())
            return
        
        # Fallback cho TikTok TTS
        self.log("⚠️ TikTok TTS đang được phát triển, dùng Edge TTS tạm thời", "WARNING")
        self.generate_edge_voice(text, output_path, "Nam Minh (Nam - Edge)", speed)
    
    def cancel_tts(self):
        """Hủy tạo giọng"""
        if self.is_processing:
            self.cancel_event.set()
            self.log("⛔ Đang hủy tạo giọng...", "WARNING")
            self.tts_cancel_btn.configure(state="disabled", text="⏳ Đang hủy...")
    
    # ========== GHÉP VIDEO VỚI TẤT CẢ TÍNH NĂNG ==========
    
    def start_render(self):
        """Bắt đầu ghép video với tất cả tính năng"""
        # Kiểm tra các file
        if not self.video_path or not os.path.exists(self.video_path):
            messagebox.showwarning("Cảnh báo", "Chưa có video nguồn!")
            return
        
        srt_to_use = self.translated_srt_path or self.srt_path
        if not srt_to_use or not os.path.exists(srt_to_use):
            messagebox.showwarning("Cảnh báo", "Chưa có phụ đề!")
            return
        
        if not self.audio_path or not os.path.exists(self.audio_path):
            messagebox.showwarning("Cảnh báo", "Chưa tạo giọng!")
            return
        
        self.is_processing = True
        self.cancel_event.clear()
        self.render_btn.configure(state="disabled", text="⏳ Đang ghép...")
        self.render_cancel_btn.configure(state="normal")
        self.update_status("⏳ Đang ghép video...", "yellow")
        self.update_progress(0)
        
        self.log("🎬 Bắt đầu ghép video với tất cả tính năng...", "PROGRESS")
        
        def render_thread():
            try:
                output_dir = self.output_dir_var.get()
                os.makedirs(output_dir, exist_ok=True)
                
                output_path = os.path.join(
                    output_dir,
                    f"reup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                )
                
                ffmpeg_path = shutil.which('ffmpeg')
                if not ffmpeg_path:
                    raise Exception("Không tìm thấy FFmpeg!")
                
                # ===== BƯỚC 1: XỬ LÝ ÂM THANH =====
                self.log("🔊 Xử lý âm thanh...", "PROGRESS")
                audio_filter = self.build_audio_filter()
                
                temp_audio = os.path.join(output_dir, "temp_audio_processed.wav")
                cmd_audio = [
                    ffmpeg_path, '-y',
                    '-i', self.audio_path,
                    '-af', audio_filter,
                    temp_audio
                ]
                subprocess.run(cmd_audio, check=True, capture_output=True)
                self.update_progress(0.2)
                
                # ===== BƯỚC 2: XỬ LÝ PHỤ ĐỀ =====
                self.log("📝 Xử lý phụ đề...", "PROGRESS")
                subtitle_filter = self.build_subtitle_filter(srt_to_use)
                
                # ===== BƯỚC 3: GHÉP VIDEO + AUDIO + PHỤ ĐỀ =====
                self.log("🎬 Ghép video và audio...", "PROGRESS")
                temp_video = os.path.join(output_dir, "temp_video_audio.mp4")
                
                # Filter complex
                filters = []
                
                # Video + Audio
                filters.append(f"[0:v]setpts=PTS-STARTPTS[video]")
                filters.append(f"[1:a]asetpts=PTS-STARTPTS[audio]")
                
                # Phụ đề
                if subtitle_filter:
                    filters.append(f"[video]{subtitle_filter}[video_sub]")
                    video_out = "[video_sub]"
                else:
                    video_out = "[video]"
                
                # Ghép
                filter_complex = ";".join(filters)
                
                cmd_merge = [
                    ffmpeg_path, '-y',
                    '-i', self.video_path,
                    '-i', temp_audio,
                    '-filter_complex', filter_complex,
                    '-map', video_out,
                    '-map', '[audio]',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    temp_video
                ]
                subprocess.run(cmd_merge, check=True, capture_output=True)
                self.update_progress(0.5)
                
                # ===== BƯỚC 4: THÊM LOGO =====
                if self.logo_path and os.path.exists(self.logo_path):
                    self.log("🎨 Thêm logo...", "PROGRESS")
                    
                    logo_settings = self.get_logo_settings()
                    temp_with_logo = os.path.join(output_dir, "temp_with_logo.mp4")
                    
                    # Lấy kích thước video
                    probe_cmd = [
                        ffmpeg_path, '-i', temp_video,
                        '-f', 'null', '-'
                    ]
                    probe = subprocess.run(probe_cmd, capture_output=True, text=True)
                    
                    # Tìm kích thước
                    match = re.search(r'(\d+)x(\d+)', probe.stderr)
                    if match:
                        video_w, video_h = int(match.group(1)), int(match.group(2))
                    else:
                        video_w, video_h = 1920, 1080
                    
                    # Tính toán vị trí logo
                    logo_size = self.logo_settings.get('size', 120)
                    logo_w = logo_size
                    logo_h = int(logo_w * 9 / 16)
                    
                    positions = {
                        'top-left': f"x=20:y=20",
                        'top-right': f"x={video_w - logo_w - 20}:y=20",
                        'bottom-left': f"x=20:y={video_h - logo_h - 20}",
                        'bottom-right': f"x={video_w - logo_w - 20}:y={video_h - logo_h - 20}",
                        'center': f"x={video_w//2 - logo_w//2}:y={video_h//2 - logo_h//2}"
                    }
                    
                    pos = positions.get(self.logo_settings.get('position', 'top-right'), "x=20:y=20")
                    opacity = self.logo_settings.get('opacity', 100) / 100
                    
                    cmd_logo = [
                        ffmpeg_path, '-y',
                        '-i', temp_video,
                        '-i', self.logo_path,
                        '-filter_complex',
                        f"[1:v]scale={logo_w}:{logo_h},format=rgba,colorchannelmixer=aa={opacity}[logo];"
                        f"[0:v][logo]overlay={pos}:eof_action=repeat:shortest=0",
                        '-c:a', 'copy',
                        temp_with_logo
                    ]
                    subprocess.run(cmd_logo, check=True, capture_output=True)
                    
                    # Thay thế file tạm
                    os.remove(temp_video)
                    temp_video = temp_with_logo
                    
                self.update_progress(0.7)
                
                # ===== BƯỚC 5: THÊM TEXT CHẠY =====
                if self.rolling_text_var.get().strip():
                    self.log("📝 Thêm text chạy...", "PROGRESS")
                    rolling_text = self.build_rolling_text()
                    temp_with_rolling = os.path.join(output_dir, "temp_with_rolling.mp4")
                    
                    cmd_rolling = [
                        ffmpeg_path, '-y',
                        '-i', temp_video,
                        '-vf', rolling_text,
                        '-c:a', 'copy',
                        temp_with_rolling
                    ]
                    subprocess.run(cmd_rolling, check=True, capture_output=True)
                    
                    os.remove(temp_video)
                    temp_video = temp_with_rolling
                
                self.update_progress(0.8)
                
                # ===== BƯỚC 6: THÊM TEXT CỐ ĐỊNH =====
                if self.fixed_text_var.get().strip():
                    self.log("📌 Thêm text cố định...", "PROGRESS")
                    fixed_text = self.build_fixed_text()
                    temp_with_fixed = os.path.join(output_dir, "temp_with_fixed.mp4")
                    
                    cmd_fixed = [
                        ffmpeg_path, '-y',
                        '-i', temp_video,
                        '-vf', fixed_text,
                        '-c:a', 'copy',
                        temp_with_fixed
                    ]
                    subprocess.run(cmd_fixed, check=True, capture_output=True)
                    
                    os.remove(temp_video)
                    temp_video = temp_with_fixed
                
                self.update_progress(0.9)
                
                # ===== BƯỚC 7: XUẤT CUỐI CÙNG =====
                # Copy file cuối
                shutil.move(temp_video, output_path)
                
                # Xóa file tạm
                if os.path.exists(temp_audio):
                    os.remove(temp_audio)
                
                self.output_path = output_path
                self.log(f"✅ Đã ghép video thành công: {output_path}", "SUCCESS")
                self.update_status("✅ Ghép video thành công", "green")
                self.update_progress(1.0)
                
                self.after(0, lambda: messagebox.showinfo(
                    "Thành công",
                    f"Video đã được ghép thành công!\nLưu tại: {output_path}\n"
                    f"🎨 Logo: {'Có' if self.logo_path else 'Không'}\n"
                    f"📝 Text chạy: {'Có' if self.rolling_text_var.get() else 'Không'}\n"
                    f"📌 Text cố định: {'Có' if self.fixed_text_var.get() else 'Không'}"
                ))
                
            except Exception as e:
                if "hủy" in str(e).lower():
                    self.log("⛔ Đã hủy ghép video", "WARNING")
                    self.update_status("⛔ Đã hủy", "orange")
                else:
                    self.log(f"❌ Lỗi ghép video: {e}", "ERROR")
                    self.update_status("❌ Lỗi", "red")
                    import traceback
                    traceback.print_exc()
            
            finally:
                self.is_processing = False
                self.render_btn.configure(state="normal", text="🎬 Bắt Đầu Ghép Video")
                self.render_cancel_btn.configure(state="disabled")
        
        threading.Thread(target=render_thread, daemon=True).start()
    
    def build_audio_filter(self):
        """Xây dựng filter cho âm thanh"""
        filters = []
        
        # Volume
        volume = self.volume_slider.get() / 100
        if volume != 1.0:
            filters.append(f"volume={volume:.2f}")
        
        # Bass và Treble (sử dụng equalizer)
        bass = self.bass_slider.get()
        treble = self.treble_slider.get()
        if bass != 0 or treble != 0:
            # Sử dụng filter equalizer đơn giản
            if bass != 0:
                freq = 100
                gain = bass * 2
                filters.append(f"aequalizer={freq}:width=200:gain={gain}")
            if treble != 0:
                freq = 5000
                gain = treble * 2
                filters.append(f"aequalizer={freq}:width=1000:gain={gain}")
        
        # Fade In
        fade_in = float(self.fade_in_var.get() or 0)
        if fade_in > 0:
            filters.append(f"afade=t=in:st=0:d={fade_in}")
        
        # Fade Out
        fade_out = float(self.fade_out_var.get() or 0)
        if fade_out > 0:
            filters.append(f"afade=t=out:st={fade_out}:d={fade_out}")
        
        # Noise Reduction
        if self.noise_reduction_var.get():
            filters.append("afftdn=nr=25:nf=-25")
        
        return ",".join(filters) if filters else "anull"
    
    def build_subtitle_filter(self, srt_path):
        """Xây dựng filter cho phụ đề"""
        # Đọc cài đặt
        font = self.font_var.get()
        font_size = self.font_size_var.get()
        color = self.subtitle_settings['color']
        outline_color = self.subtitle_settings['outline_color']
        outline_width = self.outline_width_var.get()
        shadow_offset = self.shadow_offset_var.get()
        position = self.position_var.get()
        margin = self.margin_var.get()
        
        # Xây dựng subtitle filter
        srt_path_escaped = srt_path.replace('\\', '/').replace(':', '\\:')
        
        # Các tham số
        params = [
            f"subtitles={srt_path_escaped}",
            f"force_style='Fontname={font},Fontsize={font_size},"
            f"PrimaryColour=&H{self.hex_to_ass(color)},"
            f"OutlineColour=&H{self.hex_to_ass(outline_color)},"
            f"Outline={outline_width},"
            f"Shadow={shadow_offset}'"
        ]
        
        # Vị trí
        if position == 'top':
            params.append("subtitle_top")
        elif position == 'center':
            params.append("subtitle_center")
        
        # Margin
        params.append(f"margin_v={margin}")
        
        return ",".join(params)
    
    def build_rolling_text(self):
        """Xây dựng filter cho text chạy"""
        text = self.rolling_text_var.get()
        speed = self.rolling_speed_slider.get()
        direction = self.rolling_dir_var.get()
        
        # Tạo văn bản
        escaped_text = text.replace("'", "\\'")
        
        # Tính toán di chuyển
        if direction == 'left':
            move = f"x=w+50-t*{speed}:y=h-100"
        elif direction == 'right':
            move = f"x=-w-50+t*{speed}:y=h-100"
        elif direction == 'up':
            move = f"x=50:y=h+50-t*{speed}"
        elif direction == 'down':
            move = f"x=50:y=-h-50+t*{speed}"
        else:
            move = "x=w+50-t*50:y=h-100"
        
        return f"drawtext=text='{escaped_text}':fontcolor=white:fontsize=30:fontfile=Arial:{move}"
    
    def build_fixed_text(self):
        """Xây dựng filter cho text cố định"""
        text = self.fixed_text_var.get()
        position = self.fixed_pos_var.get()
        size = self.fixed_size_var.get()
        opacity = self.fixed_opacity_var.get()
        
        escaped_text = text.replace("'", "\\'")
        
        # Vị trí
        positions = {
            'top-left': 'x=20:y=20',
            'top-right': 'x=w-tw-20:y=20',
            'bottom-left': 'x=20:y=h-th-20',
            'bottom-right': 'x=w-tw-20:y=h-th-20',
            'center': 'x=(w-tw)/2:y=(h-th)/2'
        }
        pos = positions.get(position, 'x=20:y=20')
        
        # Alpha
        alpha = float(opacity) / 100
        
        return f"drawtext=text='{escaped_text}':fontcolor=white:fontsize={size}:fontfile=Arial:{pos}:alpha={alpha}"
    
    def get_logo_settings(self):
        """Lấy cài đặt logo"""
        return {
            'position': self.logo_pos_var.get(),
            'size': int(self.logo_size_var.get()),
            'opacity': int(self.logo_opacity_slider.get())
        }
    
    def update_voice_list(self):
        """Cập nhật danh sách giọng theo engine"""
        engine = self.engine_var.get()
        
        if engine == "piper":
            voices = list(PIPER_VOICES.keys())
        elif engine == "edge":
            voices = list(EDGE_VOICES.keys())
        elif engine == "tiktok":
            voices = list(TIKTOK_VOICES.keys())
        else:
            voices = list(PIPER_VOICES.keys())
        
        self.voice_menu.configure(values=voices)
        if voices:
            self.voice_var.set(voices[0])
            self.update_voice_info()
    
    def update_voice_info(self):
        """Cập nhật thông tin giọng"""
        voice_name = self.voice_var.get()
        voice_info = ALL_VOICES.get(voice_name, {})
        
        if voice_info:
            info_text = f"{voice_info.get('desc', '')} | {voice_info.get('lang', '')} | {voice_info.get('gender', '')}"
            self.voice_info_label.configure(text=info_text)
    
    def update_speed_label(self, value):
        """Cập nhật label tốc độ"""
        self.speed_label.configure(text=f"{float(value):.1f}x")
    
    def cancel_render(self):
        """Hủy ghép video"""
        if self.is_processing:
            self.cancel_event.set()
            self.log("⛔ Đang hủy ghép video...", "WARNING")
            self.render_cancel_btn.configure(state="disabled", text="⏳ Đang hủy...")
    
    # ========== HÀM TIỆN ÍCH ==========
    
    @staticmethod
    def format_srt_time(seconds):
        """Định dạng thời gian SRT"""
        total_ms = max(0, int(round(float(seconds) * 1000)))
        h, remainder = divmod(total_ms, 3600000)
        m, remainder = divmod(remainder, 60000)
        s, ms = divmod(remainder, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    @staticmethod
    def hex_to_ass(hex_color):
        """Chuyển đổi màu HEX sang ASS format"""
        # Bỏ # nếu có
        hex_color = hex_color.lstrip('#')
        
        # ASS sử dụng định dạng BBGGRR
        if len(hex_color) == 6:
            r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
            return f"{b}{g}{r}"
        return hex_color

if __name__ == "__main__":
    app = ReupToolPro()
    app.mainloop()
