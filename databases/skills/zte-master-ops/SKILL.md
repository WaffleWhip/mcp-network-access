---
name: zte-master-operations
description: ULTIMATE OPERATIONAL GUIDE for ZTE OLT (C300/C600). Covers Hardware Audit, Triple Play Provisioning (OMCI), and Deep Troubleshooting. No bloat, pure technical data.
vendor:
  olt: ZTE
  model: [C300, C220, C600]
  platform: ZXROS
tags: [audit, provisioning, troubleshooting, zte]
---

# ZTE OLT Master Operations Guide

## 1. Hardware Audit & Health Check
- **Inventory & Soft**: `show system-group`, `show version-running`
- **Slot/Card Status**: `show card` (Check for 'INSERVICE')
- **Environment**: `show card-temperature rack 1 shelf 1`, `show card-power`
- **Performance**: `show processor`, `show mac`

## 2. Provisioning Mandates (ADN-Core)
### !!! CRITICAL ID RULE !!!
- **MANDATORY**: First available ID (1, 2, 3...) per port.
- **CONSISTENCY**: `TCONT == GEM == VPORT == Service-Port`.
- **DISCOVERY**: Use `show gpon onu state gpon-olt_{if}` to find free IDs.

---

## 3. Triple Play Provisioning (OMCI Based)

### Step 1: Registration
```bash
# Registration
interface gpon-olt_{if}
  onu {id} type {type} sn {sn}
exit
interface gpon-onu_{if}:{id}
  name {name}
```

### Step 2: VoIP (Voice)
```bash
# OLT Level
interface gpon-onu_{if}:{id}
  tcont 1 name VOIP profile UP-1M
  gemport 1 name VOIP tcont 1
  service-port 1 vport 1 user-vlan {vlan_voip} vlan {vlan_voip}
  dhcpv4-l2-relay-agent enable vport 1

# OMCI Level
pon-onu-mng gpon-onu_{if}:{id}
  service VOIP gemport 1 vlan {vlan_voip}
  voip protocol sip
  voip-ip mode dhcp vlan-profile batchVlan{vlan_voip} host 2
  sip-service pots_0/1 profile {sip_prof} userid {tel} username {tel}@realm password {pass}
```

### Step 3: Internet (HSI)
```bash
# OLT Level
interface gpon-onu_{if}:{id}
  tcont 2 name INTERNET profile {up}
  gemport 2 name INTERNET tcont 2
  service-port 2 vport 2 user-vlan {vlan_hsi} vlan {vlan_hsi}
  port-identification format DSL-FORUM-PON vport 2
  pppoe-intermediate-agent enable vport 2

# OMCI Level
pon-onu-mng gpon-onu_{if}:{id}
  service INTERNET gemport 2 vlan {vlan_hsi}
  wan-ip 1 mode pppoe username {user} password {pass} vlan-profile wan{vlan_hsi} host 1
  wan 1 service internet host 1
```

### Step 4: IPTV (UseeTV)
```bash
# OLT Level
interface gpon-onu_{if}:{id}
  tcont 3 name USEETV profile UP-512K
  gemport 3 name USEETV tcont 3
  service-port 3 vport 3 user-vlan 111 vlan 111 

# OMCI Level
pon-onu-mng gpon-onu_{if}:{id}
  service USEETV gemport 3 vlan 111
  vlan port eth_0/4 mode hybrid def-vlan 111
  mvlan 110
  mvlan tag eth_0/4 strip
igmp mvlan 110 receive-port gpon-onu_{if}:{id} vport 3
```

---

## 4. Deep Troubleshooting & Validation
- **Signal**: `show pon power attenuation gpon-onu_{if}:{id}` (-28 to -8 dBm).
- **Service Status**:
    - **Internet**: `show gpon remote-onu wan-ip {if}:{id}`
    - **Voice**: `show gpon remote-onu voip-linestatus {if}:{id}`
- **MAC Integrity**: `show mac gpon onu {if}:{id}`
- **Profile Check**: `show gpon profile tcont {name}`, `show gpon profile traffic {name}`

