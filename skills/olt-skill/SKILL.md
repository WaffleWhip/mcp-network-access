---
name: olt
description: Manage OLTs via telnet. 3 tools only: telnet, command, inventory.
---

# OLT Skill

## Tools

```
telnet(action, host?, value?, seconds?)
command(action, host?, syntax?, hint?, description?)
inventory(action, name?, host?, user?, password?, vendor?, model?)
```

---

## telnet

| Action | Params | Case |
|--------|--------|------|
| `create` | `host` | single OLT session |
| `send` | `host`, `value` | command atau button |
| `wait` | `host`, `seconds` | set wait (default 1s) |
| `status` | `host` | check session state |
| `buttons` | - | list valid buttons |

### Cases

```python
# ✅ BENAR
telnet(action="create", host="10.0.0.1")
telnet(action="send", host="10.0.0.1", value="show version")
telnet(action="send", host="10.0.0.1", value="admin,password123")
telnet(action="send", host="10.0.0.1", value="(SPACE)")
telnet(action="send", host="10.0.0.1", value="cmd1,cmd2,cmd3")
telnet(action="wait", host="10.0.0.1", seconds=1.0)
telnet(action="status", host="10.0.0.1")
telnet(action="buttons")

# ❌ SALAH
telnet(action="send", host="10.0.0.1", value="show version\n")      # extra \n
telnet(action="send", host="10.0.0.1", value="admin, password")       # space after comma
telnet(action="send", host="10.0.0.1", value="( space )")            # space inside parens
telnet(action="send", host="10.0.0.1", value="( space )")             # wrong button format
telnet(action="send", host="10.0.0.1", value="[SPACE]")               # wrong brackets
```

---

## command

| Action | Params | Case |
|--------|--------|------|
| `list` | `host`, `syntax?` | list all / get one |
| `save` | all fields | save new command |
| `update` | `host`, `syntax` | update existing |
| `delete` | `host`, `syntax` | delete command |

### Cases

```python
# ✅ BENAR - list
command(action="list", host="10.0.0.1")                          # all syntaxes
command(action="list", host="10.0.0.1", syntax="show version")  # full details

# ✅ BENAR - save (ALL fields required, no credentials)
command(action="save", host="10.0.0.1", syntax="show ont info",
        hint="show ont info 0/1/0 1", description="Show ONT info")

# ❌ SALAH - save
command(action="save", host="10.0.0.1", syntax="show ont info",
        hint="", description="")                                # hint/desc empty
command(action="save", host="10.0.0.1", syntax="login",
        hint="admin,secret123", description="Login")            # CREDENTIALS EXPOSED!

# ✅ BENAR - update
command(action="update", host="10.0.0.1", syntax="show ont info",
        hint="show ont info 0/2/0 5")

# ✅ BENAR - delete
command(action="delete", host="10.0.0.1", syntax="show ont info")
```

---

## inventory

| Action | Params | Case |
|--------|--------|------|
| `list` | `name?` | list all / get one |
| `save` | all fields | add new OLT |
| `update` | `name` | update existing |
| `delete` | `host` | delete OLT |

### Cases

```python
# ✅ BENAR - list
inventory(action="list")                               # all names
inventory(action="list", name="OLT_01")              # full details

# ✅ BENAR - save (ALL fields required)
inventory(action="save", name="OLT_01", host="10.0.0.1",
          user="admin", password="admin123",
          vendor="VendorX", model="ModelY")

# ❌ SALAH - save
inventory(action="save", name="OLT_01", host="10.0.0.1",
          user="admin", password="admin123")          # missing vendor, model

# ✅ BENAR - update
inventory(action="update", name="OLT_01", password="newpass")

# ✅ BENAR - delete
inventory(action="delete", host="10.0.0.1")
```

---

## Command Discovery (General)

```
1. Check DB first
   command(action="list", host="10.0.0.1") → syntax already saved?

2. If NOT in DB → explore with "?"
   telnet(action="send", host="10.0.0.1", value="?")
   telnet(action="send", host="10.0.0.1", value="cmd ?")
   telnet(action="send", host="10.0.0.1", value="cmd sub ?")
   ...

3. Execute discovered command
   telnet(action="send", host="10.0.0.1", value="full syntax")

4. MANDATORY → Save to DB
   command(action="save", host="10.0.0.1", syntax="...", hint="...", description="...")
```

### Exploration Example

```
telnet(action="send", host="10.0.0.1", value="?")
  → shows: show, config, display, interface, ...

telnet(action="send", host="10.0.0.1", value="display ?")
  → shows: device, ont, version, mac-address, ...

telnet(action="send", host="10.0.0.1", value="display ont ?")
  → shows: info, optical-info, status, ...

telnet(action="send", host="10.0.0.1", value="display ont optical-info ?")
  → shows: <port> <ont-id>

# Found! Execute:
telnet(action="send", host="10.0.0.1", value="display ont optical-info 0/1/0 1")

# Save (MANDATORY):
command(action="save", host="10.0.0.1", syntax="display ont optical-info",
        hint="display ont optical-info 0/1/0 1", description="Show ONT optical info")
```

---

## Buttons

```python
# ✅ BENAR
telnet(action="send", host="10.0.0.1", value="(SPACE)")    # page down
telnet(action="send", host="10.0.0.1", value="(Q)")         # quit
telnet(action="send", host="10.0.0.1", value="(ENTER)")    # newline
telnet(action="send", host="10.0.0.1", value="(TAB)")      # autocomplete

# ❌ SALAH - invalid button returns error + valid list
telnet(action="send", host="10.0.0.1", value="(entr)")      # wrong
telnet(action="send", host="10.0.0.1", value="[SPACE]")    # wrong brackets
telnet(action="send", host="10.0.0.1", value="SPACE")      # no brackets
```

---

## Pagination

```python
# Quit early (best for long output)
telnet(action="send", host="10.0.0.1", value="show running-config,(Q)")

# Page through manually
telnet(action="send", host="10.0.0.1", value="show running-config")
telnet(action="send", host="10.0.0.1", value="(SPACE)")    # next page
telnet(action="send", host="10.0.0.1", value="(Q)")         # quit
```

---

## Wait Time

| OLT | Wait |
|-----|------|
| Fast | 0.5 - 1.0 |
| Slow | 1.0 |
| Default | 1.0 |

```python
# Set for session
telnet(action="wait", host="10.0.0.1", seconds=1.0)
```

---

## Flowchart

```
Ask to do something on OLT
  │
  ├─ inventory(action="list") → get host IP
  │
  ├─ telnet(action="create", host="IP")
  │
  ├─ telnet(action="send", value="user,pass") → login
  │
  ├─ command(action="list", host="IP") → command in DB?
  │     │
  │     ├─ YES → use hint directly
  │     │
  │     └─ NO → explore with "?" → save to DB
  │
  └─ telnet(action="send", value="hint")
```
