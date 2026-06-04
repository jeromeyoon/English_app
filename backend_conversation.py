from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

app = FastAPI(title="English Conversation Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConversationRequest(BaseModel):
    words: list[str] = Field(default_factory=list)
    scene: str = ""
    mode: str = "question"
    input: str = ""
    grade: int = 1
    turns: int = 0
    history: list[dict[str, str]] = Field(default_factory=list)


class ConversationResponse(BaseModel):
    success: bool = True
    source: str = "local"
    corrected: str
    reply: str
    nextQuestion: str
    tip: str
    usedWords: list[str] = Field(default_factory=list)


def clean_word(word: str) -> str:
    return re.sub(r"[^a-z]", "", str(word).lower()).strip()


def normalize_words(words: list[str]) -> list[str]:
    out: list[str] = []
    for word in words:
        cleaned = clean_word(word)
        if cleaned and cleaned not in out:
            out.append(cleaned)
    return out[:20]


def capitalize_sentence(text: str, question: bool = False) -> str:
    text = re.sub(r"\s+", " ", str(text).strip())
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    text = re.sub(r"[?.!]+$", "", text)
    return text + ("?" if question else ".")


def correct_question(text: str) -> str:
    value = re.sub(r"[?.!]", "", text.lower()).strip()
    replacements = {
        "what is dog doing": "what is the dog doing",
        "what is boy doing": "what is the boy doing",
        "where is dog": "where is the dog",
        "where is boy": "where is the boy",
    }
    value = replacements.get(value, value)
    value = re.sub(r"\bwhat is ([a-z]+) doing\b", r"what is the \1 doing", value)
    value = re.sub(r"\bwhere is ([a-z]+)\b", r"where is the \1", value)
    if not re.match(r"^(what|where|who|is|are|do|does|can|how|why|when|which)\b", value):
        value = "what do you see"
    return capitalize_sentence(value, question=True)


def correct_answer(text: str) -> str:
    value = re.sub(r"[?.!]", "", text.lower()).strip()
    replacements = {
        "the boy play ball": "the boy is playing with a ball",
        "boy play ball": "the boy is playing with a ball",
        "dog play ball": "the dog is playing with a ball",
        "i see dog": "i see a dog",
        "i like dog": "i like dogs",
        "i like apple": "i like apples",
    }
    value = replacements.get(value, value)
    value = re.sub(r"\bi see ([a-z]+)\b", r"i see a \1", value)
    value = re.sub(r"\b([a-z]+) play ([a-z]+)\b", r"the \1 is playing with a \2", value)
    return capitalize_sentence(value)


def infer_scene_parts(words: list[str]) -> dict[str, str]:
    def pick(candidates: list[str], fallback: str) -> str:
        for candidate in candidates:
            if candidate in words:
                return candidate
        return fallback

    action = pick(["play", "run", "eat", "read", "write", "go", "make", "take"], "play")
    action_ing = {
        "play": "playing",
        "run": "running",
        "eat": "eating",
        "read": "reading",
        "write": "writing",
        "go": "going",
        "make": "making",
        "take": "taking",
    }.get(action, "playing")
    return {
        "subject": pick(["boy", "girl", "student", "teacher", "friend"], "boy"),
        "animal": pick(["dog", "cat", "bird", "fish"], "dog"),
        "place": pick(["park", "school", "home", "class", "room", "zoo", "farm"], "park"),
        "object": pick(["ball", "book", "apple", "pencil", "toy", "desk", "bag"], "ball"),
        "action": action_ing,
    }


def answer_question(corrected: str, parts: dict[str, str]) -> str:
    lower = corrected.lower()
    if "doing" in lower and parts["animal"] in lower:
        return f"The {parts['animal']} is {parts['action']} with a {parts['object']}."
    if "doing" in lower:
        return f"The {parts['subject']} is {parts['action']} with a {parts['object']}."
    if "where" in lower:
        return f"The {parts['animal']} is in the {parts['place']}."
    if "what do you see" in lower:
        return f"I see a {parts['animal']}, a {parts['subject']}, and a {parts['object']}."
    if "do you like" in lower:
        return f"Yes, I like the {parts['object']}."
    return f"Good question. I see a {parts['animal']} in the {parts['place']}."


def next_question(turn_count: int, parts: dict[str, str]) -> str:
    questions = [
        f"What is the {parts['subject']} doing?",
        f"Where is the {parts['animal']}?",
        f"What do you see in the {parts['place']}?",
        f"Do you like the {parts['object']}?",
        "Can you ask me one question about the picture?",
    ]
    return questions[turn_count % len(questions)]


def make_tip(original: str, corrected: str, mode: str) -> str:
    if original.strip() == corrected.strip():
        return "좋아요. 자연스러운 문장입니다."
    if mode == "question":
        return "질문에서는 명사 앞에 the/a를 넣으면 더 자연스럽습니다."
    if " is playing " in corrected.lower():
        return "동작을 말할 때는 be동사 + ing 형태를 쓰면 자연스럽습니다."
    return "명사 앞의 a/the와 동사 형태를 확인해 보세요."


def local_response(payload: ConversationRequest) -> ConversationResponse:
    words = normalize_words(payload.words)
    parts = infer_scene_parts(words)
    mode = "answer" if payload.mode == "answer" else "question"
    corrected = correct_question(payload.input) if mode == "question" else correct_answer(payload.input)
    reply = answer_question(corrected, parts) if mode == "question" else f"Good. {corrected}"
    used_words = [word for word in re.findall(r"[a-z]+", corrected.lower()) if word in words]
    return ConversationResponse(
        source="local",
        corrected=corrected,
        reply=reply,
        nextQuestion=next_question(payload.turns, parts),
        tip=make_tip(payload.input, corrected, mode),
        usedWords=list(dict.fromkeys(used_words)),
    )


def extract_output_text(data: dict[str, Any]) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def openai_response(payload: ConversationRequest) -> ConversationResponse | None:
    if not OPENAI_API_KEY:
        return None

    local = local_response(payload)
    system_prompt = (
        "You are an English tutor for an elementary learner. "
        "Use only short, natural English. The learner may ask a question or answer a question. "
        "Correct grammar gently, answer based on the scene, and ask one next question. "
        "Return only JSON with keys: corrected, reply, nextQuestion, tip, usedWords. "
        "tip must be Korean and concise. usedWords must be a JSON array."
    )
    user_prompt = {
        "words": normalize_words(payload.words),
        "scene": payload.scene,
        "mode": payload.mode,
        "learnerInput": payload.input,
        "grade": payload.grade,
        "history": payload.history[-8:],
        "fallbackExample": local.model_dump(),
    }
    body = {
        "model": OPENAI_MODEL,
        "instructions": system_prompt,
        "input": json.dumps(user_prompt, ensure_ascii=False),
        "text": {"format": {"type": "json_object"}},
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
        text = extract_output_text(json.loads(raw))
        parsed = json.loads(text)
        return ConversationResponse(
            source="openai",
            corrected=str(parsed.get("corrected") or local.corrected),
            reply=str(parsed.get("reply") or local.reply),
            nextQuestion=str(parsed.get("nextQuestion") or local.nextQuestion),
            tip=str(parsed.get("tip") or local.tip),
            usedWords=normalize_words(parsed.get("usedWords") or local.usedWords),
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError):
        return None


@app.post("/conversation", response_model=ConversationResponse)
def conversation(payload: ConversationRequest) -> ConversationResponse:
    ai_result = openai_response(payload)
    if ai_result:
        return ai_result
    return local_response(payload)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "openaiConfigured": bool(OPENAI_API_KEY),
        "model": OPENAI_MODEL,
    }
