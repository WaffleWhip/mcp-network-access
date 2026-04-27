"""Virtual Terminal - Telnet via telnetlib3 with persistent sessions"""
import telnetlib3, asyncio, re

SESSIONS = {}

def clean(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    text = re.sub(r'\x1B\[[0-9;]*[a-zA-Z]', '', text)
    return text.replace('\x00', '').strip()

async def _recv(r, t=1.0, size=4096):
    b = ""
    for _ in range(30):
        try:
            ch = await asyncio.wait_for(r.read(size), timeout=t)
            b += ch or ""
            t = 0.5
        except:
            break
    return b

async def login(host, port=23, username=None, password=None, enable_pwd=None, wait=2):
    key = host.upper()
    if key in SESSIONS:
        try:
            SESSIONS[key]["w"].close()
        except:
            pass
        del SESSIONS[key]

    r, w = await telnetlib3.open_connection(host, port or 23, encoding='ascii')
    out = ""

    if username:
        await asyncio.sleep(wait)
        await _recv(r, t=1)
        w.write(f"{username}\n"); await w.drain()

    if password:
        await asyncio.sleep(wait)
        await _recv(r, t=1)
        w.write(f"{password}\n"); await w.drain()
        result = await _recv(r)
        out += result

        if ">" in result and "#" not in result:
            w.write("enable\n"); await w.drain()
            await asyncio.sleep(wait)
            result = await _recv(r)
            out += result

            if enable_pwd and "password" in result.lower():
                w.write(f"{enable_pwd}\n"); await w.drain()
                await asyncio.sleep(wait)
                out += await _recv(r)

    SESSIONS[key] = {"r": r, "w": w, "user": username}
    return clean(out)

async def send_command(host, command=None, commands=None, wait=2):
    key = host.upper()
    if key not in SESSIONS:
        return None, "NOT_LOGGED_IN"

    r, w = SESSIONS[key]["r"], SESSIONS[key]["w"]
    out = ""

    cmd_list = []
    if command:
        cmd_list.append(command)
    if commands:
        cmd_list.extend(commands)

    for cmd in cmd_list:
        await asyncio.sleep(wait)
        w.write(f"{cmd}\n"); await w.drain()
        result = await _recv(r, t=2)
        out += result

        if "{ <cr>" in result or "--more--" in result.lower() or ("{" in result and "|" in result):
            if "--more--" in result.lower():
                w.write("q")
            else:
                w.write("")
            await w.drain()
            await asyncio.sleep(wait)
            out += await _recv(r, t=2)

    await asyncio.sleep(wait)
    out += await _recv(r, t=2)

    return clean(out), ""

async def send_button(host, button="q", wait=2):
    key = host.upper()
    if key not in SESSIONS:
        return None, "NOT_LOGGED_IN"

    r, w = SESSIONS[key]["r"], SESSIONS[key]["w"]
    w.write(button); await w.drain(); await asyncio.sleep(wait)
    result = await _recv(r)
    return clean(result), ""

def is_logged_in(host):
    return host.upper() in SESSIONS

def close_session(host):
    key = host.upper()
    if key in SESSIONS:
        try:
            SESSIONS[key]["w"].close()
        except:
            pass
        del SESSIONS[key]