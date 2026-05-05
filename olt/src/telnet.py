"""OLT Manager - Telnet Driver (Last Output Only)"""

import os, yaml, telnetlib3, asyncio, re, time
from pathlib import Path
from typing import Optional, Dict, Any, List

SESSIONS: Dict[str, Any] = {}

BUTTONS_FILE = Path(__file__).parent.parent / "storage" / "buttons.yaml"


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


async def _read_until_silence(host, timeout=15.0, silence_gap=0.5):
    key = host.upper()
    if key not in SESSIONS:
        return ""

    r = SESSIONS[key]["r"]
    buffer = ""
    start_time = time.time()
    last_data_time = time.time()
    last_line_has_content = False

    try:
        while (time.time() - start_time) < timeout:
            try:
                chunk = await asyncio.wait_for(r.read(4096), timeout=0.2)
                if chunk:
                    buffer += chunk
                    last_data_time = time.time()
                    lines = buffer.strip().split("\n")
                    if lines:
                        last_line = lines[-1].strip()
                        last_line_has_content = bool(last_line)
                else:
                    break
            except asyncio.TimeoutError:
                if (
                    buffer
                    and last_line_has_content
                    and (time.time() - last_data_time) >= silence_gap
                ):
                    return buffer
                continue
    except Exception:
        pass
    return buffer


async def connect(host, port=23):
    key = host.upper()
    if key in SESSIONS:
        try:
            SESSIONS[key]["w"].write("\n")
            await SESSIONS[key]["w"].drain()
            banner = await _read_until_silence(host, timeout=2)
            SESSIONS[key]["last_activity"] = time.time()
            SESSIONS[key]["last_output"] = clean(banner)
            return clean(banner)
        except:
            pass

    r, w = await telnetlib3.open_connection(host, port or 23, encoding="ascii")
    SESSIONS[key] = {
        "r": r,
        "w": w,
        "last_activity": time.time(),
        "last_output": "",
        "last_cmd": "",
        "last_id": 0,
        "wait_time": 1.0,
    }
    banner = await _read_until_silence(host, timeout=5)
    SESSIONS[key]["last_output"] = clean(banner)
    return clean(banner)


async def send_command(host, command=None, commands=None):
    key = host.upper()
    if key not in SESSIONS:
        return None, "NOT_CONNECTED"

    wait = SESSIONS[key].get("wait_time", 1.0)
    r, w = SESSIONS[key]["r"], SESSIONS[key]["w"]
    out = ""
    items = commands if commands else ([command] if command else [])
    btn_map = get_btn_map()

    cmd_id = SESSIONS[key]["last_id"]

    for item in items:
        stripped = str(item).strip()
        cmd_id += 1

        if stripped.startswith("(") and stripped.endswith(")"):
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

        if wait > 0:
            await asyncio.sleep(wait)

        res = await _read_until_silence(host, timeout=20.0)
        out += res

        SESSIONS[key]["last_id"] = cmd_id
        SESSIONS[key]["last_activity"] = time.time()
        SESSIONS[key]["last_output"] = clean(out)

    return clean(out), ""


def get_status(host: str) -> dict:
    key = host.upper()
    if key not in SESSIONS:
        return {"connected": False, "host": host}

    session = SESSIONS[key]
    last_output = clean(session.get("last_output", ""))
    return {
        "connected": True,
        "host": host,
        "last_id": session.get("last_id", 0),
        "last_cmd": session.get("last_cmd", ""),
        "last_output": last_output,
        "last_activity": session.get("last_activity"),
    }


def set_wait(host: str, seconds: float):
    key = host.upper()
    if key in SESSIONS:
        SESSIONS[key]["wait_time"] = seconds
    return {"host": host, "wait_time": seconds}


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
