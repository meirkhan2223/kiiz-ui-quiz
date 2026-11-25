#!/usr/bin/env python3
"""Айгүл мен Дәулет (Microsoft, қазақша) дауыстарын utterances.json бойынша жасайды.
Қажет: pip install edge-tts.   Іске қосу: python3 voice/edge_voices.py
Файл аты = мәтіннің хэші (сайттағы textHash), сондықтан мәтін өзгерсе — жаңа файл жасалады."""
import asyncio, json, os, edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = [("kk-KZ-AigulNeural", "aigul"), ("kk-KZ-DauletNeural", "daulet")]


async def one(sem, voice, folder, key, text):
    path = os.path.join(HERE, folder, f"{key}.mp3")
    if os.path.exists(path):
        return
    async with sem:
        await edge_tts.Communicate(text, voice, rate="-6%").save(path)


async def main():
    texts = json.load(open(os.path.join(HERE, "utterances.json"), encoding="utf-8"))
    sem = asyncio.Semaphore(6)
    jobs = []
    for voice, folder in VOICES:
        os.makedirs(os.path.join(HERE, folder), exist_ok=True)
        keep = {f"{k}.mp3" for k in texts}
        for f in os.listdir(os.path.join(HERE, folder)):  # remove recordings of texts that no longer exist
            if f.endswith(".mp3") and f not in keep:
                os.remove(os.path.join(HERE, folder, f))
        jobs += [one(sem, voice, folder, k, t) for k, t in texts.items()]
    await asyncio.gather(*jobs)
    print("Дайын:", len(texts), "мәтін ×", len(VOICES), "дауыс")


asyncio.run(main())
