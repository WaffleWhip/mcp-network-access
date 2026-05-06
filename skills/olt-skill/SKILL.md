---
name: olt
description: Manage OLTs via telnet. Individual tools for easy enable/disable.
---

# OLT Skill

## Tools (14 total)

```
telnet_create, telnet_send, telnet_wait, telnet_status, telnet_buttons
command_list, command_save, command_update, command_delete
inventory_list, inventory_save, inventory_update, inventory_delete
```

---

## telnet_create

```python
# Create new telnet session
telnet_create(host="10.0.0.1")
```

---

## telnet_send

```python
# Single command
telnet_send(host="10.0.0.1", value="show version")

# Login
telnet_send(host="10.0.0.1", value="admin,password123")

# Batch commands
telnet_send(host="10.0.0.1", value="cmd1,cmd2,cmd3")

# Button press
telnet_send(host="10.0.0.1", value="(SPACE)")
telnet_send(host="10.0.0.1", value="(Q)")

# Quit pagination early
telnet_send(host="10.0.0.1", value="show running-config,(Q)")

# ❌ SALAH
telnet_send(host="10.0.0.1", value="show version\n")    # extra \n
telnet_send(host="10.0.0.1", value="admin, password")    # space after comma
telnet_send(host="10.0.0.1", value="( space )")          # wrong parens
```

---

## telnet_wait

```python
# Set wait time (default 1.0s)
telnet_wait(host="10.0.0.1", seconds=1.0)
```

---

## telnet_status

```python
# Check session state
telnet_status(host="10.0.0.1")
```

---

## telnet_buttons

```python
# List valid buttons
telnet_buttons()
```

---

## command_list

```python
# List all commands (syntax only)
command_list(host="10.0.0.1")

# Get specific command (returns hint + description)
command_list(host="10.0.0.1", syntax="show version")
```

---

## command_save

```python
# ALL fields required, no credentials
command_save(
    host="10.0.0.1",
    syntax="show ont info",
    hint="show ont info 0/1/0 1",
    description="Show ONT info"
)

# ❌ SALAH
command_save(host="10.0.0.1", syntax="login", hint="admin,secret123")  # CREDENTIALS!
```

---

## command_update

```python
# syntax required, hint/description optional
command_update(host="10.0.0.1", syntax="show ont info", hint="show ont info 0/2/0 5")
```

---

## command_delete

```python
command_delete(host="10.0.0.1", syntax="show ont info")
```

---

## inventory_list

```python
# List all OLTs
inventory_list()

# Get specific OLT (returns full details)
inventory_list(name="OLT_01")
```

---

## inventory_save

```python
# ALL fields required
inventory_save(
    name="OLT_01",
    host="10.0.0.1",
    user="admin",
    password="admin123",
    vendor="Huawei",
    model="MA5800"
)
```

---

## inventory_update

```python
# name required, others optional
inventory_update(name="OLT_01", password="newpass")
```

---

## inventory_delete

```python
inventory_delete(host="10.0.0.1")
```

---

## Command Discovery

```
1. command_list(host) → check if command exists
2. If NOT → explore with "?"
   telnet_send(host, value="?")
   telnet_send(host, value="cmd ?")
   telnet_send(host, value="cmd sub ?")
3. Execute discovered command
4. MANDATORY → command_save(...)
```

---

## Buttons

```python
# ✅ BENAR
telnet_send(host="10.0.0.1", value="(SPACE)")   # page down
telnet_send(host="10.0.0.1", value="(Q)")        # quit
telnet_send(host="10.0.0.1", value="(ENTER)")    # newline
telnet_send(host="10.0.0.1", value="(TAB)")      # autocomplete

# ❌ SALAH
telnet_send(host="10.0.0.1", value="(entr)")    # wrong
telnet_send(host="10.0.0.1", value="[SPACE]")  # wrong brackets
```

---

## Wait Time

| OLT | Wait |
|-----|------|
| Fast | 0.5 - 1.0 |
| Slow (ZTE C600) | 1.0 |
| Default | 1.0 |

---

## Flowchart

```
Ask to do something on OLT
  │
  ├─ inventory_list() → get host
  │
  ├─ telnet_create(host)
  │
  ├─ telnet_send(value="user,pass") → login
  │
  ├─ command_list(host) → in DB?
  │     │
  │     ├─ YES → use hint
  │     └─ NO → explore with "?" → command_save(...)
  │
  └─ telnet_send(value="hint")
```
