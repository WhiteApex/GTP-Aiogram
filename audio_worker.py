import os
import wave
import json
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

def convert_audio(input_path, output_path):
    # Загружаем аудиофайл .ogg
    audio = AudioSegment.from_ogg(input_path)

    # Приводим к моно, 16-бит PCM и 16000 Гц
    audio = audio.set_channels(1)  # Моно
    audio = audio.set_frame_rate(16000)  # Частота дискретизации 16000 Гц
    audio = audio.set_sample_width(2)  # 16-бит (2 байта)

    # Сохраняем преобразованный файл в формате .wav
    audio.export(output_path, format="wav")
    
def audio_to_text(path_audio=str) -> str:
    model_path = "model/vosk-model-small-ru-0.22"
    input_audio_path = path_audio
    output_audio_path = "new_audio.wav"

    convert_audio(input_audio_path, output_audio_path)

    if not os.path.exists(model_path):
        print("Модель не найдена.")
        exit(1)

    model = Model(model_path)
    wf = wave.open(output_audio_path, "rb")
    rec = KaldiRecognizer(model,16000)

    # Проверка параметров аудиофайла
    '''print("Channels:", wf.getnchannels())
    print("Sample width:", wf.getsampwidth())
    print("Frame rate:", wf.getframerate())
    '''
    
    l = []
    full_text = ""
    count = 0
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            count+=1
            result = rec.Result()
            accept_text = json.loads(result)["text"]
            l.append(accept_text)
            #print("Accepted result:", result)
        else:
            partial_result = rec.PartialResult()
            #print("Partial result:", partial_result)
            partial_text = json.loads(partial_result)["partial"]
    

    final_result = rec.FinalResult()
    if final_result:
        try:
            print(final_result)
            l.append(json.loads(final_result)["text"])
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON.")
    else:
        print("Результат пустой.")
    
    return(l)