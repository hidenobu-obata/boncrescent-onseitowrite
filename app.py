import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from io import BytesIO
from dotenv import load_dotenv
import uvicorn

# 環境変数の読み込み
load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# テンプレートと静的ファイルの設定
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. ルートパス（フロントエンド表示）
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # 最新のFastAPIに対応した呼び出し方
    return templates.TemplateResponse(request=request, name="index.html")

# 2. ヘルスチェック（UptimeRobot用）
@app.get("/health")
async def health():
    return {"status": "ok"}

# 3. アップロード・文字起こしAPI
@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        if not file:
            return JSONResponse(status_code=400, content={"error": "ファイルを選択してください"})
        
        if not file.filename.endswith(".mp3"):
            return JSONResponse(status_code=400, content={"error": "mp3のファイルではありません"})
        
        contents = await file.read()
        # 15分相当のサイズチェック（概算）
        if len(contents) > 25 * 1024 * 1024:
            return JSONResponse(status_code=400, content={"error": "変換は15分までです"})

        audio_stream = BytesIO(contents)
        audio_stream.name = "audio.mp3"
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_stream
        )
        return {"text": transcript.text}

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(status_code=500, content={"error": "システムエラー"})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)