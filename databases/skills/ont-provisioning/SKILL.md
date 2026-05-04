---
name: ont-open-provision
description: FTTH provisioning skill for OPEN network — OLT ZTE C300 and ONT Fiberhome HG6145F via GenieACS TR069. Use when activating new ONT, registering ONT to OLT, or provisioning FTTH services (internet/VOICE/IPTV).
vendor:
  olt: ZTE
  model-olt: C300
  ont: Fiberhome
  model-ont: HG6145F
  network: GPON OPEN
  provisioning-side: both
tags:
  - ftth
  - gpon
  - zte
  - fiberhome
  - tr069
  - provisioning
---

# ONT Open Provision

FTTH service provisioning for OPEN network — covering both OLT and ONT sides.

## Workflow

**OLT Side (ZTE C300):**
1. [[references/olt/zte-c300 | OLT ZTE C300]] → Register ONT by Serial Number
2. [[references/olt/zte-c300 | OLT ZTE C300]] → Configure services (VOIP/INTERNET/IPTV VLANs)

**ONT Side (Fiberhome HG6145F):**
3. [[references/ont/fiberhome-hg6145f/hsi | HSI Internet]] → WAN VLAN, PPPoE credentials
4. [[references/ont/fiberhome-hg6145f/voice | VOICE VoIP]] → SIP proxy, registrar (REQUIRED)
5. [[references/ont/fiberhome-hg6145f/iptv | IPTV USEETV]] → WAN VLAN, multicast VLAN

6. Validate → Online status, optical power (-28 to -8 dBm)

## Quick Reference

| Service | User VLAN | S-VLAN | Gemport | TCONT Profile |
|---------|-----------|--------|---------|---------------|
| VOIP | 100 | 501 | 1 | UP-1M |
| INTERNET | 200 | 2250 | 2 | UP-45056KA3 |
| IPTV | 111 | 111 | 3 | UP-512K |

## Rules

- **VOICE required** — always configure even for internet-only
- **SN case-sensitive** — match ONT sticker exactly
- **Max 64 ONTs/port** — verify slot availability
- **Model-specific** — HG6145F parameters only

## Validation Checklist

- [ ] Order status = APPROVED
- [ ] ONT Serial Number verified
- [ ] GPON port has free slot
- [ ] ONT registered on OLT
- [ ] ONT online (`show gpon onu state <port>`)
- [ ] Optical power OK (-28 to -8 dBm)
- [ ] Services up (HSI, VOICE, IPTV)
- [ ] Customer connectivity confirmed

## Provisioning Report

```markdown
## OPEN Provisioning Report
**Customer:** <NAME> | **Order ID:** <ORDER_ID>
**ONT SN:** <SERIAL_NUMBER>
**ONT Model:** Fiberhome HG6145F
**GPON Port:** <rack>/<port>/<olt_port>:<onu_id>
**Services:** HSI | VOICE | IPTV

**OLT Status:** Registered / Failed
**ONT Status:** Online / Offline
**Optical Power:** <x> dBm
**Result:** SUCCESS / FAILED
```

## References

**OLT:**
- [[references/olt/zte-c300 | OLT ZTE C300]] — GPON OLT commands, VLAN config, validation

**ONT Fiberhome HG6145F:**
- [[references/ont/fiberhome-hg6145f/hsi | HSI]] — Internet WAN VLAN, PPPoE credentials
- [[references/ont/fiberhome-hg6145f/voice | VOICE]] — VoIP SIP parameters (REQUIRED)
- [[references/ont/fiberhome-hg6145f/iptv | IPTV]] — IPTV WAN VLAN, multicast VLAN

## Source Files

| File | Description |
|------|-------------|
| `../CONTOH COMMAND Provisioning Open - OLT ZTE C300.txt` | Original OLT ZTE C300 command reference |
| `../tr069 parameter set Open ONT Fiberhome HG6145F.xlsx` | Original TR069 parameter spreadsheet |
