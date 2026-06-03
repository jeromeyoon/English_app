# 영어 학습 앱 + OCR 설정 가이드

## 1단계: Google Cloud Vision API 설정

### 1.1 Google Cloud 계정 및 프로젝트 생성
1. https://console.cloud.google.com/ 접속
2. 우측 상단 드롭다운 → "새 프로젝트"
3. 프로젝트 이름: `english-app` (자유)
4. "만들기" 클릭

### 1.2 Cloud Vision API 활성화
1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. 검색창에 `Cloud Vision API` 입력
3. 검색 결과에서 "Cloud Vision API" 클릭
4. "활성화" 버튼 클릭

### 1.3 서비스 계정 키 발급
1. 좌측 메뉴 → "API 및 서비스" → "서비스 계정"
2. "서비스 계정 만들기"
   - 서비스 계정 이름: `ocr-app`
   - 서비스 계정 ID: 자동 채워짐
   - "만들고 계속" 클릭
3. "권한 부여" 단계 (선택사항) → 지나가기
4. "완료"

### 1.4 JSON 키 다운로드
1. 만든 서비스 계정 클릭
2. "키" 탭 → "새 키 추가" → "JSON"
3. 다운로드된 파일을 프로젝트 폴더에 저장
   - 예: `C:\Users\vmax8\Documents\Claude\Projects\English_app\credentials.json`

---

## 2단계: 로컬 환경 설정

### 2.1 파이썬 설치 확인
```bash
python --version
```
(Python 3.8 이상 필요)

### 2.2 필수 패키지 설치
명령 프롬프트에서:
```bash
cd C:\Users\vmax8\Documents\Claude\Projects\English_app
pip install -r requirements.txt
```

### 2.3 backend.py 수정
`backend.py` 파일을 열고 아래 라인 수정:

```python
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/credentials.json'
```

↓↓↓ 다음과 같이 수정:

```python
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\vmax8\Documents\Claude\Projects\English_app\credentials.json'
```

---

## 3단계: 앱 실행

### 3.1 백엔드 시작
명령 프롬프트에서:
```bash
cd C:\Users\vmax8\Documents\Claude\Projects\English_app
python -m uvicorn backend:app --reload --port 8000
```

출력이 나타나면:
```
Uvicorn running on http://127.0.0.1:8000
```

### 3.2 프론트엔드 열기
1. `app.html` 파일을 웹 브라우저에서 열기
   - 또는: 파일 탐색기에서 더블클릭
2. "🖼️ 파일 선택" 또는 "📷 카메라" 버튼 클릭

---

## 테스트 체크리스트

- [ ] 백엔드 (python 명령) 실행 중
- [ ] 브라우저에서 `app.html` 열림
- [ ] "🖼️ 파일 선택" 버튼 작동
- [ ] 영어 텍스트 있는 이미지 선택
- [ ] 단어가 자동으로 단어 목록에 추가됨
- [ ] "🎲 문장 만들기" 버튼으로 새 단어 문장 생성

---

## 문제해결

### "연결 오류" 표시
- 백엔드가 실행 중인지 확인
- 명령 프롬프트에서 `python -m uvicorn backend:app --reload --port 8000` 다시 실행

### "카메라 접근 불가"
- 브라우저에 카메라 권한 부여 필요
- 또는 HTTPS 연결 필요 (로컬: `localhost`는 일반적으로 OK)

### Google Vision API 오류
- `credentials.json` 경로 다시 확인
- Google Cloud에서 Vision API 활성화 확인
- 서비스 계정에 "Viewer" 이상의 권한이 있는지 확인

---

## 월 한도 및 비용

- **무료**: 매월 1,000개 이미지
- **유료**: 그 이후 이미지당 $1.50

학습용이므로 무료로 충분할 가능성 높음.
