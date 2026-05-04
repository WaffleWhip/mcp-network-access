"""OLT Manager - Telnet Driver (Raw Silence + Line Buffer)"""

import telnetlib3, asyncio, re, time
from typing import Optional, Dict, Any, List

SESSIONS: Dict[str, Any] = {}


def clean(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="ignore")
    # Remove ANSI escape sequences
    text = re.sub(r"\x1B\[[0-9;]*[a-zA-Z]", "", text)
    # Normalize line endings: \r\n -> \n and remove lonely \r
    text = text.replace("\r\n", "\n").replace("\r", "")
    # Remove non-printable chars (except \n and \t)
    text = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\t")
    return text.strip()


async def _read_until_silence(host, timeout=15.0, silence_gap=0.5):
    """Event-driven: Reads until last line has content + silence, or timeout."""
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
                    SESSIONS[key]["rolling_buffer"] = (
                        SESSIONS[key].get("rolling_buffer", "") + chunk
                    )[-5000:]
                    last_data_time = time.time()

                    # Check if last line has content (non-blank)
                    lines = buffer.strip().split("\n")
                    if lines:
                        last_line = lines[-1].strip()
                        last_line_has_content = bool(last_line)
                else:
                    break
            except asyncio.TimeoutError:
                # Only return if: buffer has content, last line non-blank, and silence_gap passed
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
            return banner
        except:
            pass

    r, w = await telnetlib3.open_connection(host, port or 23, encoding="ascii")
    SESSIONS[key] = {
        "r": r,
        "w": w,
        "last_activity": time.time(),
        "rolling_buffer": "",
        "preferred_length": 20,  # Default
    }
    banner = await _read_until_silence(host, timeout=5)
    return banner


async def send_command(host, command=None, commands=None):
    key = host.upper()
    if key not in SESSIONS:
        return None, "NOT_CONNECTED"
    r, w = SESSIONS[key]["r"], SESSIONS[key]["w"]
    out = ""
    items = commands if commands else ([command] if command else [])
    btn_map = {
        "[ENTER]": "\n",
        "[SPACE]": " ",
        "[Q]": "q",
        "[QUIT]": "q",
        "[ESC]": "\x1b",
        "[TAB]": "\t",
    }

    for item in items:
        # Auto-detect button: starts with [ and ends with ]
        stripped = str(item).strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            key = stripped.upper()
            if key in btn_map:
                char = btn_map[key]
            else:
                char = f"{stripped[1:-1]}\n"  # Remove brackets, treat as command
        else:
            char = f"{stripped}\n"

        w.write(char)
        await w.drain()
        res = await _read_until_silence(host, timeout=20.0)
        out += res

    SESSIONS[key]["last_activity"] = time.time()
    return clean(out), ""


async def send_button(host, button="enter"):
    key = host.upper()
    if key not in SESSIONS:
        return None, "NOT_CONNECTED"
    r, w = SESSIONS[key]["r"], SESSIONS[key]["w"]
    btn_map = {"space": " ", "enter": "\n", "q": "q", "esc": "\x1b", "tab": "\t"}
    w.write(btn_map.get(button.lower(), "\n"))
    await w.drain()
    res = await _read_until_silence(host, timeout=5)
    SESSIONS[key]["last_activity"] = time.time()
    return clean(res), ""


def get_last_buffer(host: str, lines: Optional[int] = None):
    key = host.upper()
    raw = SESSIONS.get(key, {}).get("rolling_buffer", "")
    cleaned = clean(raw)
    if not cleaned:
        return ""

    # Use session preference if lines not provided
    limit = (
        lines
        if lines is not None
        else SESSIONS.get(key, {}).get("preferred_length", 20)
    )

    lines_list = cleaned.split("\n")
    return "\n".join(lines_list[-limit:])


def set_preferred_length(host: str, length: int):
    key = host.upper()
    if key in SESSIONS:
        SESSIONS[key]["preferred_length"] = length


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
