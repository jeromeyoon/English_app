from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import base64
import re

# Gemini API 키 설정
API_KEY = "API Key "  # ← 여기에 API 키 입력
genai.configure(api_key=API_KEY)

app = FastAPI()

# CORS 설정
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
    이미지 파일을 받아서 Gemini로 텍스트 인식
    """
    try:
        # 파일 읽기
        image_data = await file.read()

        # base64로 인코딩
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")

        # 파일 타입 결정
        file_ext = file.filename.lower().split('.')[-1]
        mime_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        mime_type = mime_type_map.get(file_ext, 'image/jpeg')

        # Gemini 모델로 텍스트 추출
        model = genai.GenerativeModel('gemini-2.5-flash')

        message = model.generate_content([
            "이미지에서 보이는 모든 영어 단어를 추출해줘. 쉼표로 구분된 단어 목록으로만 응답해줘. 예: apple, book, cat, dog",
            {
                "mime_type": mime_type,
                "data": image_base64
            }
        ])

        response_text = message.text.strip()

        # 응답에서 단어 파싱 (쉼표 또는 공백으로 분리)
        words = re.split(r'[,\s]+', response_text)
        words = [w.lower().strip() for w in words if w.strip() and len(w) > 1]

        # 중복 제거, 영어 단어만 필터링
        seen = set()
        filtered_words = []
        for word in words:
            clean_word = re.sub(r'[^a-z]', '', word.lower())
            if clean_word and clean_word not in seen:
                filtered_words.append(clean_word)
                seen.add(clean_word)

        return {
            "success": True,
            "fullText": response_text,
            "words": filtered_words,
            "count": len(filtered_words)
        }

    except Exception as e:
        return {"success": False, "message": f"오류: {str(e)}"}

@app.get("/health")
def health():
    """헬스 체크"""
    return {"status": "ok"}
