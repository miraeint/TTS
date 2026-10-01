"""
Gemini TTS Service Engine
- Google GenAI SDK를 활용한 음성 합성 비즈니스 로직
- PCM -> WAV 인메모리 컨테이너 변환
- 30종 공식 화자(Voice) 지원 및 장문(최대 10,000자) 지원
"""

import os
import io
import wave
import base64
from typing import Optional, Dict, Tuple
from google import genai
from google.genai import errors

# Gemini 공식 지원 30종 화자 목록 및 특성 매핑
AVAILABLE_VOICES: Dict[str, str] = {
    "Kore": "차분하고 단호한 톤 (Firm)",
    "Puck": "경쾌하고 활기찬 톤 (Upbeat)",
    "Charon": "신뢰감 있고 정보 전달에 적합한 톤 (Informative)",
    "Fenrir": "열정적이고 흥분된 톤 (Excitable)",
    "Aoede": "산뜻하고 자연스러운 톤 (Breezy)",
    "Leda": "젊고 생동감 있는 톤 (Youthful)",
    "Zephyr": "밝고 맑은 톤 (Bright)",
    "Orus": "중후하고 또렷한 톤 (Firm)",
    "Achernar": "부드럽고 편안한 톤 (Soft)",
    "Sulafat": "따뜻하고 친근한 톤 (Warm)",
    "Alnilam": "안정적이고 묵직한 톤 (Firm)",
    "Sadachbia": "생기발랄한 톤 (Lively)",
    "Callirrhoe": "편안하고 여유로운 톤 (Easy-going)",
    "Autonoe": "밝고 통통 튀는 톤 (Bright)",
    "Enceladus": "숨소리가 섞인 감성적인 톤 (Breathy)",
    "Iapetus": "명료하고 선명한 톤 (Clear)",
    "Umbriel": "담담하고 편안한 톤 (Easy-going)",
    "Algieba": "부드럽고 매끄러운 톤 (Smooth)",
    "Despina": "차분하고 매끄러운 톤 (Smooth)",
    "Erinome": "깨끗하고 청명한 톤 (Clear)",
    "Algenib": "거칠고 개성 있는 허스키 톤 (Gravelly)",
    "Rasalgethi": "차분한 설명형 톤 (Informative)",
    "Laomedeia": "밝고 긍정적인 톤 (Upbeat)",
    "Schedar": "차분하고 일정한 톤 (Even)",
    "Gacrux": "성숙하고 깊이 있는 톤 (Mature)",
    "Pulcherrima": "직접적이고 당당한 톤 (Forward)",
    "Achird": "친절하고 다정한 톤 (Friendly)",
    "Zubenelgenubi": "편안하고 일상적인 톤 (Casual)",
    "Vindemiatrix": "부드럽고 온화한 톤 (Gentle)",
    "Sadaltager": "지적이고 학구적인 톤 (Knowledgeable)"
}

# 지원 모델 목록
AVAILABLE_MODELS = {
    "gemini-3.1-flash-tts-preview": "Gemini 3.1 Flash TTS (공식 음성 합성 전용 모델 - 추천)",
    "gemini-3.8-flash": "Gemini 3.8 Flash (최신 멀티모달 플래시 모델)"
}

class TTSError(Exception):
    """TTS 처리 중 발생하는 도메인 예외"""
    def __init__(self, message: str, code: str = "TTS_ERROR"):
        super().__init__(message)
        self.code = code


def validate_text(text: str, max_length: int = 10000) -> str:
    """
    입력 텍스트를 검증 및 정제합니다. (기본 10,000자까지 지원)
    """
    if not text or not text.strip():
        raise TTSError("음성으로 변환할 텍스트를 1자 이상 입력해주세요.", code="EMPTY_INPUT")
    
    cleaned = text.strip()
    if len(cleaned) > max_length:
        raise TTSError(f"텍스트 길이가 최대 허용치({max_length:,}자)를 초과했습니다. (현재 {len(cleaned):,}자)", code="TEXT_TOO_LONG")
    
    return cleaned


def pcm_to_wav(pcm_bytes: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> bytes:
    """
    Gemini API에서 반환하는 Raw PCM 오디오를 브라우저 재생 및 저장 가능한 표준 WAV 포맷으로 변환합니다.
    """
    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_bytes)
    return wav_io.getvalue()


def generate_tts_audio(
    text: str,
    voice: str = "Kore",
    model: str = "gemini-3.1-flash-tts-preview",
    api_key: Optional[str] = None,
    max_length: int = 10000
) -> Tuple[bytes, Dict[str, any]]:
    """
    Gemini API를 호출하여 텍스트를 음성으로 변환하고 WAV 바이너리를 반환합니다.
    """
    # 1. 텍스트 유효성 검사 (최대 10,000자)
    sanitized_text = validate_text(text, max_length=max_length)

    # 2. API Key 확인
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise TTSError(
            "Gemini API Key가 설정되지 않았습니다. 사이드바에 입력하거나 .env 파일에 GEMINI_API_KEY를 등록해주세요.",
            code="API_KEY_MISSING"
        )

    # 3. Client 초기화
    try:
        client = genai.Client(api_key=key)
    except Exception as e:
        raise TTSError(f"Gemini 클라이언트 초기화 실패: {str(e)}", code="CLIENT_INIT_FAILED")

    # 4. API 요청 생성 및 호출
    try:
        interaction = client.interactions.create(
            model=model,
            input=sanitized_text,
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": voice}
                ]
            }
        )
    except errors.APIError as e:
        status_code = getattr(e, "code", None)
        err_msg = str(e)
        if status_code in (401, 403) or "API_KEY_INVALID" in err_msg:
            raise TTSError("API Key가 유효하지 않거나 권한이 없습니다. API 키를 다시 확인해주세요.", code="AUTH_FAILED")
        elif status_code == 429 or "RESOURCE_EXHAUSTED" in err_msg:
            raise TTSError("API 요청 한도(Quota/Rate Limit)를 초과했습니다. 잠시 후 다시 시도해주세요.", code="QUOTA_EXCEEDED")
        elif "SAFETY" in err_msg or "blocked" in err_msg.lower():
            raise TTSError("안전성 및 콘텐츠 정책에 의해 음성 생성이 차단되었습니다. 텍스트 내용을 수정해주세요.", code="SAFETY_BLOCKED")
        else:
            raise TTSError(f"Gemini API 오류 ({status_code}): {err_msg}", code="API_ERROR")
    except Exception as e:
        err_str = str(e)
        if "timeout" in err_str.lower():
            raise TTSError("네트워크 연결 시간이 초과되었습니다. 인터넷 연결을 확인해주세요.", code="TIMEOUT")
        raise TTSError(f"음성 생성 중 오류가 발생했습니다: {err_str}", code="UNKNOWN_ERROR")

    # 5. 오디오 데이터 추출 및 WAV 인코딩
    output_audio = getattr(interaction, "output_audio", None)
    if not output_audio or not output_audio.data:
        raise TTSError("모델로부터 오디오 스트림을 수신하지 못했습니다. (빈 응답)", code="EMPTY_AUDIO_RESPONSE")

    pcm_data = base64.b64decode(output_audio.data)
    wav_bytes = pcm_to_wav(pcm_data, channels=1, rate=24000, sample_width=2)

    metadata = {
        "model": model,
        "voice": voice,
        "input_length": len(sanitized_text),
        "pcm_bytes_size": len(pcm_data),
        "wav_bytes_size": len(wav_bytes)
    }

    return wav_bytes, metadata
