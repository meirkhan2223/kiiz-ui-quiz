#!/usr/bin/env python3
"""ElevenLabs арқылы презентацияның барлық мәтінін MP3-ке айналдыру.

Қолдану:
  export ELEVENLABS_API_KEY="кілтіңіз"
  python3 voice/elevenlabs.py --list            # дауыстар тізімі (voice_id)
  python3 voice/elevenlabs.py VOICE_ID          # барлық 53 файлды жасау
  python3 voice/elevenlabs.py VOICE_ID --only s4,a17   # тек кейбірін қайта жасау
  python3 voice/elevenlabs.py VOICE_ID --force  # барлығын қайтадан жасау

Файлдар voice/eleven/<id>.mp3 болып сақталады, сайт оларды өзі ойнатады.
"""
import json, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "eleven")
API = "https://api.elevenlabs.io/v1"
MODEL = os.environ.get("ELEVEN_MODEL", "eleven_v3")  # v3 қазақ тілін қолдайды


def key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not k:
        sys.exit("ELEVENLABS_API_KEY орнатылмаған. Алдымен: export ELEVENLABS_API_KEY=\"кілтіңіз\"")
    return k


def req(url, data=None):
    headers = {"xi-api-key": key(), "Accept": "audio/mpeg" if data else "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=120)


def list_voices():
    with req(f"{API}/voices") as r:
        for v in json.load(r)["voices"]:
            print(f'{v["voice_id"]}  {v["name"]}  ({v.get("category","")})')


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__); return
    if args[0] == "--list":
        list_voices(); return
    voice = args[0]
    force = "--force" in args
    only = None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    texts = json.load(open(os.path.join(HERE, "utterances.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    todo = [(k, t) for k, t in texts.items() if (only is None or k in only)]
    for n, (k, text) in enumerate(todo, 1):
        path = os.path.join(OUT, f"{k}.mp3")
        if os.path.exists(path) and not force and only is None:
            print(f"[{n}/{len(todo)}] {k} бар, өткізілді"); continue
        body = {"text": text, "model_id": MODEL,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        for attempt in range(4):
            try:
                with req(f"{API}/text-to-speech/{voice}?output_format=mp3_44100_128", body) as r:
                    open(path, "wb").write(r.read())
                print(f"[{n}/{len(todo)}] {k} ✓"); break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="ignore")[:300]
                if e.code == 429 and attempt < 3:
                    time.sleep(5 * (attempt + 1)); continue
                sys.exit(f"{k}: қате {e.code}: {msg}")
    print(f"Дайын! Файлдар: {OUT}")


if __name__ == "__main__":
    main()
