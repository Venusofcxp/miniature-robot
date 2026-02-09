from flask import Flask, jsonify
import requests
import threading
import time
import re

app = Flask(__name__)

BASE = "https://www.bestblaze.com.br"

cache = {
    "double": [],
    "crash": [],
}

# ================= TOKEN =================

def get_token(session):
    try:
        r = session.get(BASE, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        match = re.search(r"_token:\s*'([^']+)'", r.text)
        if match:
            return match.group(1)
    except Exception as e:
        print("Erro token:", e)
    return None


# ================= DOUBLE =================

def worker_double():
    session = requests.Session()  # <<< sessão exclusiva
    global cache

    while True:
        try:
            token = get_token(session)
            if token:
                r = session.post(
                    f"{BASE}/jogadasDouble",
                    data={"ini": 1, "_token": token},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=10
                )

                data = r.json()
                if data:
                    cache["double"] = data
                    print("✅ Double atualizado")

        except Exception as e:
            print("❌ Erro double:", e)

        time.sleep(1)


# ================= CRASH =================

def worker_crash():
    session = requests.Session()  # <<< sessão exclusiva
    global cache

    while True:
        try:
            token = get_token(session)
            if token:
                r = session.post(
                    f"{BASE}/jogadasCrash",
                    data={"ini": 1, "_token": token},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=10
                )

                data = r.json()
                if data:
                    cache["crash"] = data
                    print("✅ Crash atualizado")

        except Exception as e:
            print("❌ Erro crash:", e)

        time.sleep(1)


# inicia threads
threading.Thread(target=worker_double, daemon=True).start()
threading.Thread(target=worker_crash, daemon=True).start()


# ================= ROTAS =================

@app.route("/double")
def double():
    return jsonify(cache["double"])


@app.route("/crash")
def crash():
    return jsonify(cache["crash"])


@app.route("/")
def home():
    return jsonify({"status": "online"})


# =========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
