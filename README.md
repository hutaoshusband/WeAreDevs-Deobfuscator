# WeAreDevs LuaU Deobfuscator

A toolkit for analyzing and deobfuscating Lua scripts protected by the WeAreDevs obfuscator (v1.0.0).

**Important Notice**  
This project is no longer developed publicly as open source.  
All future updates, releases, improvements, and documentation will only be available at:

https://fireflyprotector.xyz/wearedevs-deobfuscator

The project remains completely free, but it is now closed-source.

---
```md
[![Visit Website](https://img.shields.io/badge/Visit%20Website-FireflyProtector-blue?style=for-the-badge)](https://fireflyprotector.xyz/wearedevs-deobfuscator)
```



---

## Overview

The WeAreDevs Lua Deobfuscator provides tools for dynamically analyzing obfuscated Lua scripts in a mocked Roblox and exploit environment.  
Its goal is to reveal reconstructed strings, intercepted function calls, loadstring payloads, and the general behavior of obfuscated scripts by simulating the execution environment used by Roblox exploits.

---

## Tools

### 1. Dynamic Dumper (`tools/run_dumper.py`)

The primary component of this project.  
It executes obfuscated Lua inside a simulated environment defined in `tools/dumper.lua`.

**Features:**
- Mocks Roblox globals such as `game`, `workspace`, `Instance`, `Vector3`, `CFrame`, and `Drawing`.
- Mocks exploit APIs including `getgenv`, `checkcaller`, and `identifyexecutor`.
- Logs:
  - `print` and `warn` outputs
  - Notifications sent through `SetCore`
  - Loadstring calls and their resulting code
  - Large string constructions via `table.concat`
- Built to handle complex and unusual obfuscation techniques such as proxy objects and shuffled string operations.

---

### 2. Static Extractor (`tools/extract_strings.py`)

A static analysis tool that attempts to extract encoded or encrypted strings from obfuscated Lua scripts without executing them.

---

## Requirements

### Lua 5.1

Lua 5.1 is required for the dumper to run.

**Installation:**
- Ubuntu/Debian:  
  `sudo apt install lua5.1`
- macOS:  
  `brew install lua@5.1`
- Windows:  
  Download from LuaBinaries or place `lua.exe` next to `deobfuscator.exe`

---

## Installation

### Option 1: Pre-Built Binary (Windows)

Download `deobfuscator.exe` from:

https://fireflyprotector.xyz/wearedevs-deobfuscator

**Requirements:**
- `lua.exe` (Lua 5.1) must be next to the executable or available in your system PATH.

**Usage:**
1. Run `deobfuscator.exe`
2. Drag and drop your obfuscated `.lua` file
3. The output file will be created as `filename_deobfuscated.lua`

---

## Usage (Source Version)

### Analyze a single file
```bash
python3 tools/run_dumper.py path/to/obfuscated_script.lua
```

### Analyze an entire directory
```bash
python3 tools/run_dumper.py path/to/folder/
```

During execution, the dumper prints:
- Intercepted Roblox calls
- Detected loadstring usage
- Contents of dynamically generated payloads
- Large concatenated strings
- General execution logs and behaviors

---

## Example Output

```
[DUMP] game.StarterGui:SetCore("SendNotification", { ... })
[DUMP] LOADSTRING DETECTED (len=1024)
[DUMP] LOADSTRING CONTENT: print("Hello World")
```

---

## Status

| Level     | Support Status | Notes |
|-----------|----------------|-------|
| Basic     | Supported      | Standard obfuscation works reliably. |
| Hard      | Supported      | Handles more complex string rebuilding and proxy behavior. |
| Extreme   | Experimental   | May fail due to advanced VM logic or anti-tamper features. |

---

## Documentation

Additional documentation and internal notes can be found in:  
`docs/DEOBFUSCATION_NOTES.md`
