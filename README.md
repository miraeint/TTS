# 🎙️ Gemini Flash TTS Web App

Google Gemini API의 고품질 Text-to-Speech (TTS) 기능을 활용하여 텍스트를 자연스러운 음성으로 실시간 변환하고, 브라우저에서 즉시 청취 및 WAV 파일로 다운로드할 수 있는 경량 웹 애플리케이션입니다.

---

## 🌟 주요 기능

- **Google GenAI 공식 SDK 연동**: 최신 `google-genai` SDK 및 Gemini TTS 모델 지원
- **브라우저 즉시 재생 & 다운로드**: Base64 오디오 스트림을 인메모리(WAV)로 변환하여 별도 코덱 설치 없이 브라우저에서 바로 청취 및 저장
- **다양한 화자(Voice) 프리셋**: 차분한 톤(Kore), 경쾌한 톤(Puck), 정보 전달 톤(Charon) 등 다양한 보이스 지원
- **Director's Chair 연기 지시문 지원**: *"Say cheerfully: 안녕하세요!"*와 같이 감정 및 톤 제어 프롬프트 지원
- **견고한 예외 처리**: API Key 인증 실패, 쿼터 제한(429), 안전성 필터링, 공백 입력 등에 대한 사용자 친화적 에러 가이드
- **세션 상태 유지**: Streamlit 리로드 시에도 생성된 오디오 데이터 보존

---

## 🚀 빠른 시작 (Quick Start)

### 1. 환경 설정 (.env)
`.env.example`을 복사하여 `.env` 파일을 생성하고 Google AI Studio에서 발급받은 API 키를 입력합니다.

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(참고: 웹 UI 사이드바에서 직접 API 키를 입력할 수도 있습니다.)*

### 2. 가상환경 활성화 및 의존성 설치
```bash
# 가상환경 생성 (최초 1회)
python -m venv .venv

# 가상환경 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 필수 패키지 설치
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501`이 자동으로 열립니다.

---

## 📁 프로젝트 구조

```text
TEST11/
├── .env.example          # 환경변수 템플릿
├── .gitignore            # Git 제외 설정
├── requirements.txt      # 의존성 패키지 목록
├── tts_engine.py         # Gemini API 통신 및 오디오 변환 핵심 로직
├── app.py                # Streamlit UI 컴포넌트 및 이벤트 핸들링
└── README.md             # 프로젝트 안내 문서
```
