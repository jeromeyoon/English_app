from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import vision
import json
import os
import base64
from io import BytesIO

# Google Cloud 인증 (다운로드한 JSON 파일 경로 지정)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/credentials.json'  # ← 여기에 경로 입력

app = FastAPI()

# CORS 설정 (HTML에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """
    이미지 파일을 받아서 텍스트 인식
    """
    try:
        # 파일 읽기
        image_data = await file.read()

        # Google Vision API 호출
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_data)
        response = client.text_detection(image=image)

        # 텍스트 추출
        texts = response.text_annotations

        if not texts:
            return {"success": False, "message": "텍스트를 찾을 수 없습니다."}

        # 첫 번째 항목은 전체 텍스트, 나머지는 개별 단어
        full_text = texts[0].description if texts else ""

        # 개별 단어 추출 (신뢰도 필터링)
        words = []
        for text in texts[1:]:
            # 영어 단어만 추출 (대문자, 소문자, 일부 특수문자)
            word = text.description.strip()
            # 문자만 포함된 단어 필터링
            if word and any(c.isalpha() for c in word):
                words.append(word.lower())

        # 중복 제거
        words = list(dict.fromkeys(words))

        return {
            "success": True,
            "fullText": full_text,
            "words": words,
            "count": len(words)
        }

    except Exception as e:
        return {"success": False, "message": f"오류: {str(e)}"}

@app.get("/health")
def health():
    """헬스 체크"""
    return {"status": "ok"}
