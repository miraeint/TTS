"""
Gemini TTS Web Application (Streamlit)
- 브라우저 기반 실시간 텍스트 음성 변환 (TTS)
- 30종 화자 프리셋 및 최대 10,000자 지원
- 오디오 즉시 재생 및 WAV 다운로드 기능
"""

import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# 로컬 환경변수 로드
load_dotenv()

from tts_engine import (
    AVAILABLE_VOICES,
    AVAILABLE_MODELS,
    generate_tts_audio,
    TTSError
)

# 페이지 기본 설정
st.set_page_config(
    page_title="Gemini Flash TTS Studio",
    page_icon="🎙️",
    layout="centered"
)

# 세션 상태 초기화 (재실행 시 오디오 소실 방지)
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "audio_metadata" not in st.session_state:
    st.session_state.audio_metadata = None

# --- 사이드바 설정 영역 ---
with st.sidebar:
    st.header("⚙️ 환경 및 음성 설정")
    
    # 1단계 설정: API 키
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "1. Gemini API Key",
        value=env_api_key,
        type="password",
        placeholder="AIzaSy...",
        help=".env 파일에 GEMINI_API_KEY를 입력해두면 자동으로 로드됩니다."
    )
    
    st.markdown("---")
    
    # 2단계 설정: 모델 및 목소리
    st.subheader("🎙️ 모델 및 목소리 선택")
    model_keys = list(AVAILABLE_MODELS.keys())
    selected_model = st.selectbox(
        "사용 모델",
        options=model_keys,
        index=0,
        format_func=lambda k: AVAILABLE_MODELS[k]
    )
    
    voice_keys = list(AVAILABLE_VOICES.keys())
    selected_voice = st.selectbox(
        "목소리 (화자) 선택",
        options=voice_keys,
        index=0,
        format_func=lambda k: f"{k} - {AVAILABLE_VOICES[k]}"
    )

    st.markdown("---")
    st.info(
        "💡 **내 목소리 톤 연출 팁**\n"
        "자신의 실제 음색과 가장 유사한 화자(남성/여성/차분함/활기참 등)를 선택한 뒤, "
        "입력 텍스트 맨 앞에 연기 지시문을 추가하면 더욱 자연스럽게 발화합니다.\n\n"
        "예: *'차분하고 부드러운 한국어 억양으로: 안녕하세요...'* "
    )

# --- 메인 본문 영역 ---
st.title("🎙️ Gemini Flash TTS")
st.markdown("Google Gemini API를 활용하여 텍스트를 자연스러운 음성으로 실시간 변환하고 바로 재생 및 다운로드하세요.")

# --- 순번 안내: 사용 방법 가이드 ---
with st.expander("📖 사용 방법 (단계별 안내)", expanded=True):
    st.markdown("""
    1. **API 키 설정**: 좌측 사이드바에 Gemini API Key를 입력합니다. (또는 `.env` 파일에 저장)
    2. **목소리 및 모델 선택**: 좌측 사이드바에서 본인 성향에 맞는 **화자(Voice)**와 **모델**을 선택합니다.
    3. **텍스트 작성**: 아래 입력창에 음성으로 변환할 문장을 작성합니다. (최대 10,000자 지원)
    4. **음성 생성 및 다운로드**: **[🔊 음성 생성하기]** 버튼을 클릭하면 즉시 브라우저에서 재생되고 WAV 파일로 저장할 수 있습니다.
    """)

# 입력 텍스트 영역 (샘플 버튼 제거됨, 최대 10,000자)
input_text = st.text_area(
    "변환할 텍스트 입력",
    value="",
    height=200,
    placeholder="음성으로 변환할 문장을 입력하세요. (최대 10,000자)",
    max_chars=10000
)

# 텍스트 글자 수 표시
char_count = len(input_text.strip()) if input_text else 0
st.caption(f"현재 글자 수: **{char_count:,} / 10,000자**")

col_btn, _ = st.columns([1, 2])
with col_btn:
    generate_btn = st.button("🔊 음성 생성하기", type="primary", use_container_width=True)

# 생성 로직 트리거
if generate_btn:
    try:
        effective_key = api_key_input.strip() if api_key_input else None
        
        with st.spinner("Gemini API와 통신하여 고품질 음성을 생성하는 중입니다..."):
            start_time = time.time()
            wav_bytes, metadata = generate_tts_audio(
                text=input_text,
                voice=selected_voice,
                model=selected_model,
                api_key=effective_key,
                max_length=10000
            )
            elapsed_time = round(time.time() - start_time, 2)
            metadata["elapsed_seconds"] = elapsed_time

            # 세션에 캐싱
            st.session_state.audio_bytes = wav_bytes
            st.session_state.audio_metadata = metadata
            
        st.success(f"음성 생성이 완료되었습니다! (소요 시간: {elapsed_time}초)")

    except TTSError as e:
        st.error(f"⚠️ {str(e)}")
    except Exception as e:
        st.error(f"⚠️ 시스템 오류가 발생했습니다: {str(e)}")

# --- 결과 오디오 렌더링 및 다운로드 영역 ---
if st.session_state.audio_bytes is not None:
    st.markdown("---")
    st.subheader("🎧 생성된 음성 결과")
    
    # 1. 브라우저 즉시 재생
    st.audio(st.session_state.audio_bytes, format="audio/wav")
    
    # 메타데이터 정보 표시
    meta = st.session_state.audio_metadata or {}
    size_kb = round(len(st.session_state.audio_bytes) / 1024, 1)
    st.info(f"**화자**: `{meta.get('voice')}` | **모델**: `{meta.get('model')}` | **포맷**: WAV (24kHz 16-bit Mono) | **크기**: {size_kb} KB")
    
    # 2. 다운로드 버튼
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_filename = f"gemini_tts_{meta.get('voice', 'voice')}_{timestamp}.wav"
    
    st.download_button(
        label="💾 WAV 파일 다운로드",
        data=st.session_state.audio_bytes,
        file_name=download_filename,
        mime="audio/wav",
        type="secondary",
        use_container_width=True
    )
