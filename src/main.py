from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydub import AudioSegment
import os
import uuid

app = FastAPI()

def remove_file(file_path: str):
    try:
        os.remove(file_path)
    except OSError:
        pass

@app.post("/convert")
async def convert(background_tasks: BackgroundTasks, file: UploadFile = File(...), bitrate: str = "64k", sample_rate: int = 44100, channels: int = 2):
    if not file.filename.endswith('.oga'):
        raise HTTPException(status_code=400, detail="Неверный формат файла")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    ogg_file_path = os.path.join('/tmp', unique_filename)
    with open(ogg_file_path, 'wb') as f:
        f.write(await file.read())

    mp3_file_path = ogg_file_path.replace('.oga', '.mp3')
    audio = AudioSegment.from_ogg(ogg_file_path)
    audio = audio.set_frame_rate(sample_rate).set_channels(channels)
    audio.export(mp3_file_path, format='mp3', bitrate=bitrate)

    response = FileResponse(mp3_file_path, media_type='audio/mpeg', filename=os.path.basename(mp3_file_path))

    # Очистка временных файлов после отправки ответа
    background_tasks.add_task(remove_file, ogg_file_path)
    background_tasks.add_task(remove_file, mp3_file_path)

    return response

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ogg2mpeg</title>
        <link rel="icon" href="/favicon.ico" type="image/x-icon">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <h1>Ogg2mpeg Service</h1>
        <p>Этот сервис принимает аудиофайлы в формате OGA и конвертирует их в MP3.</p>
        <h2>Использование</h2>
        <p>Отправьте POST-запрос на <code>ogg2mpeg.duckdns.org:7788</code> с файлом и укажите условия в query-параметрах.</p>
        <h3>Пример запроса</h3>
        <pre>
        curl -X POST -F "file=@myFile.oga" &#92;
        "http://ogg2mpeg.duckdns.org:7788/convert?bitrate=64k&sample_rate=22050&channels=1" &#92;
        --output "myFile.mp3"
        </pre>
        <h2>Возможные параметры</h2>
        <ul>
            <li>bitrate: <strong>64k</strong>, 128k, 192k, 256k, 320k</li>
            <li>sample_rate: 8000, 22050, <strong>44100</strong>, 48000</li>
            <li>channels: 1 (моно), <strong>2 (стерео)</strong></li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7788)
