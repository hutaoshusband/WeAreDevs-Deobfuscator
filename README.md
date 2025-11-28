## WeAreDevs LuaU Deobfuscator

A toolkit for analyzing and deobfuscating Lua scripts protected by the WeAreDevs obfuscator (v1.0.0).

**Important Notice**  
This project is no longer developed publicly as open source.  
All future updates, releases, improvements, and documentation will only be available at:

https://fireflyprotector.xyz/wearedevs-deobfuscator

The project remains completely free, but it is now closed-source.

<a href="https://fireflyprotector.xyz/wearedevs-deobfuscator" target="_blank"> <img src="https://img.shields.io/badge/Visit%20Website-FireflyProtector-blue?style=for-the-badge"> </a>



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
**# WeAreDevs LuaU Deobfuscator  
### ➜ All future updates are now exclusively provided on the official website  
### ➜ Now supports additional LuaU obfuscators

A toolkit for analyzing and deobfuscating Lua/LuaU scripts originally protected by the WeAreDevs obfuscator (v1.0.0), now extended to support other LuaU obfuscation methods as well.

---

## ➜ Important Notice

This project is no longer maintained as a public open-source repository.  
From now on:

**➜ All updates  
➜ All releases  
➜ All improvements  
➜ All documentation**

are exclusively available on the official website:

**https://fireflyprotector.xyz/wearedevs-deobfuscator**

The tool remains free to use, but is now closed-source.

---

## ➜ Overview

The WeAreDevs LuaU Deobfuscator provides a combination of dynamic and static analysis utilities within a simulated Roblox + exploit environment.  
Its capabilities include reconstructing strings, analyzing reconstructed loadstring payloads, observing function calls, and understanding behavioral logic inside obfuscated scripts.

---

## ➜ Tools

### 1. Dynamic Dumper (`tools/run_dumper.py`)

Executes obfuscated Lua/LuaU code in a controlled mock environment (`tools/dumper.lua`).

**Features:**
- Mocked Roblox globals: `game`, `workspace`, `Instance`, `Vector3`, `CFrame`, `Drawing`
- Mocked exploit APIs: `getgenv`, `checkcaller`, `identifyexecutor`
- Detailed logging:
  - `print` / `warn`
  - `SetCore` notifications
  - loadstring usage and reconstructed payloads
  - large string operations from `table.concat`
- Handles complex behaviors such as proxy objects and non-standard string rebuilding.

---

### 2. Static Extractor (`tools/extract_strings.py`)

Extracts encoded or encrypted strings using static analysis without executing the script.

---

## ➜ Requirements

### Lua 5.1

Required for the dynamic dumper.

**Installation:**
- **Ubuntu/Debian:**  
  `sudo apt install lua5.1`
- **macOS:**  
  `brew install lua@5.1`
- **Windows:**  
  Use LuaBinaries or place `lua.exe` next to `deobfuscator.exe`.

---

## ➜ Installation

### Option 1: Pre-Built Binary (Windows)

Download from the official website:

**https://fireflyprotector.xyz/wearedevs-deobfuscator**

**Requirements:**
- `lua.exe` (Lua 5.1) in PATH or next to the executable

**Usage:**
1. Run `deobfuscator.exe`
2. Drag & drop your `.lua` file
3. Output will be saved as `filename_deobfuscated.lua`

---

## ➜ Usage (Source Version)

### Analyze a single file:
```bash
python3 tools/run_dumper.py path/to/obfuscated_script.lua
```

### Analyze a directory:
```bash
python3 tools/run_dumper.py path/to/folder/
```

The dumper logs:
- intercepted Roblox API calls  
- loadstring occurrences and payloads  
- reconstructed strings  
- general execution behavior  

---

## ➜ Example Output

```
[DUMP] game.StarterGui:SetCore("SendNotification", { ... })
[DUMP] LOADSTRING DETECTED (len=1024)
[DUMP] LOADSTRING CONTENT: print("Hello World")
```

---

## ➜ Support Status

| Level     | Status        | Notes |
|-----------|----------------|-------|
| Basic     | Supported      | Reliable for standard obfuscation. |
| Hard      | Supported      | Handles complex string logic and proxies. |
| Extreme   | Experimental   | May fail on VM-based or hardened obfuscation. |

---

## ➜ Documentation

Additional notes can be found in:  
`docs/DEOBFUSCATION_NOTES.md`
