# Gemini API로 OCR 설정 (간단함)

## 1단계: backend_gemini.py 수정

파일을 열고, 이 줄을:
```python
API_KEY = "YOUR_API_KEY_HERE"
```

이렇게 바꿈 (API key 붙여넣기):
```python
API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxx"
```

## 2단계: 패키지 설치

명령 프롬프트:
```bash
cd C:\Users\vmax8\Documents\Claude\Projects\English_app
pip install -r requirements_gemini.txt
```

## 3단계: 백엔드 실행

```bash
python -m uvicorn backend_gemini:app --reload --port 8000
```

출력:
```
Uvicorn running on http://127.0.0.1:8000
```

## 4단계: 앱 실행

`app.html`을 브라우저에서 열기 → "🖼️ 파일 선택" 또는 "📷 카메라"

---

## 장점
- Google Cloud 계정 설정 불필요
- API key만 있으면 바로 실행
- 비용: 무료 사용량 충분 (월 15개 무료, 그 이후 매우 저렴)

## 비용 정보
- **무료**: 매월 최대 1,500개 요청 (이미지당 1개 요청)
- 학습용이면 무료로 충분
