"""OLT Manager - Telnet Driver"""

import yaml, telnetlib3, asyncio, re, time
from pathlib import Path
from typing import Optional, Dict, Any, List

SESSIONS: Dict[str, Any] = {}

BUTTONS_FILE = Path(__file__).parent.parent / "storage" / "buttons.yaml"

GLOBAL_WAIT = 10.0


def load_buttons():
    if BUTTONS_FILE.exists():
        with open(BUTTONS_FILE) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_btn_map():
    return load_buttons()


def clean(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")
    text = re.sub(r"\x1B\[[0-9;]*[a-zA-Z]", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "")
    text = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\t")
    return text.strip()


async def _read_output(host, timeout=10.0):
    key = host.upper()
    if key not in SESSIONS:
        return ""

    r = SESSIONS[key]["r"]
    buffer = ""
    start_time = time.time()

    while (time.time() - start_time) < timeout:
        try:
            chunk = await asyncio.wait_for(r.read(4096), timeout=0.3)
            if chunk:
                buffer += chunk
            else:
                break
        except asyncio.TimeoutError:
            break

    return buffer


async def connect(host, port=23):
    key = host.upper()

    if key in SESSIONS:
        try:
            SESSIONS[key]["w"].write("\n")
            await SESSIONS[key]["w"].drain()
            banner = await _read_output(host, timeout=5.0)
            SESSIONS[key]["last_activity"] = time.time()
            SESSIONS[key]["last_output"] = clean(banner)
            SESSIONS[key]["last_cmd"] = ""
            return clean(banner)
        except:
            pass

    try:
        r, w = await asyncio.wait_for(
            telnetlib3.open_connection(host, port or 23, encoding="ascii"), timeout=10.0
        )
    except asyncio.TimeoutError:
        return "CONNECTION_TIMEOUT"

    SESSIONS[key] = {
        "r": r,
        "w": w,
        "last_activity": time.time(),
        "last_output": "",
        "last_cmd": "",
        "last_id": 0,
    }
    banner = await _read_output(host, timeout=5.0)
    SESSIONS[key]["last_output"] = clean(banner)
    return clean(banner)


async def send_command(host, command=None, commands=None, delay=0):
    key = host.upper()
    if key not in SESSIONS:
        return None, "NOT_CONNECTED"

    r, w = SESSIONS[key]["r"], SESSIONS[key]["w"]
    items = commands if commands else ([command] if command else [])
    btn_map = get_btn_map()

    cmd_id = SESSIONS[key]["last_id"]
    accumulated = ""

    for idx, item in enumerate(items):
        if idx > 0 and delay > 0:
            await asyncio.sleep(delay)

        stripped = str(item).strip()
        cmd_id += 1
        is_button = stripped.startswith("(") and stripped.endswith(")")

        if is_button:
            btn_key = stripped[1:-1].upper()
            if btn_key in btn_map:
                char = btn_map[btn_key]
            else:
                return (
                    None,
                    f"INVALID_BUTTON: {btn_key}. Valid buttons: {list(btn_map.keys())}",
                )
            w.write(char)
        else:
            w.write(stripped + "\n")
            SESSIONS[key]["last_cmd"] = stripped

        await w.drain()

        if delay > 0:
            await asyncio.sleep(delay)

        res = await _read_output(host, timeout=GLOBAL_WAIT)
        accumulated += res

        SESSIONS[key]["last_id"] = cmd_id
        SESSIONS[key]["last_activity"] = time.time()

    SESSIONS[key]["last_output"] = clean(accumulated)
    return clean(accumulated), ""


def get_status(host: str) -> str:
    key = host.upper()
    if key not in SESSIONS:
        return "error: not connected"

    session = SESSIONS[key]
    last_output_raw = session.get("last_output", "")

    return last_output_raw


def is_logged_in(host: str):
    return host.upper() in SESSIONS


def close_session(host: str):
    key = host.upper()
    if key in SESSIONS:
        try:
            SESSIONS[key]["w"].close()
        except:
            pass
        del SESSIONS[key]


async def _heartbeat():
    while True:
        await asyncio.sleep(30)
        for k, v in list(SESSIONS.items()):
            if (time.time() - v["last_activity"]) > 300:
                close_session(k)
            else:
                try:
                    v["w"].write("\n")
                    await v["w"].drain()
                except:
                    close_session(k)
