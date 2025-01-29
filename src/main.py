from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydub import AudioSegment
import os
import uuid

app = FastAPI()

def remove_file(file_path):
    try:
        os.remove(file_path)
    except OSError:
        pass

@app.post("/convert")
async def convert(file: UploadFile = File(...), bitrate: str = "64k", sample_rate: int = 44100, channels: >
    if not file.filename.endswith('.ogg'):
        raise HTTPException(status_code=400, detail="Неверный формат файла")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    ogg_file_path = os.path.join('/tmp', unique_filename)
    with open(ogg_file_path, 'wb') as f:
        f.write(await file.read())

    mp3_file_path = ogg_file_path.replace('.ogg', '.mp3')
    audio = AudioSegment.from_ogg(ogg_file_path)
    audio = audio.set_frame_rate(sample_rate).set_channels(channels)
    audio.export(mp3_file_path, format='mp3', bitrate=bitrate)

    response = FileResponse(mp3_file_path, media_type='audio/mpeg', filename=os.path.basename(mp3_file_pat>

    # Очистка временных файлов после отправки ответа
    response.call_on_close(lambda: remove_file(ogg_file_path))
    response.call_on_close(lambda: remove_file(mp3_file_path))

    return response

@app.get("/")
async def read_root():
    return {
        "message": "Этот сервис принимает аудиофайлы в формате OGG и конвертирует их в MP3.",
        "usage": "Отправьте POST-запрос на /convert с файлом и укажите параметры в query-параметрах.",
        "example": "curl -X POST -F \"file=@path/to/your/file.ogg\" \"http://your-server-address:8000/conv>
        "bitrate_options": ["64k", "128k", "192k", "256k", "320k"],
        "sample_rate_options": [22050, 44100, 48000],
        "channels_options": [1, 2]
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7788)
