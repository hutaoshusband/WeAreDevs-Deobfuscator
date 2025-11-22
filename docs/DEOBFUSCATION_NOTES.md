# Deobfuscation Findings

## Obfuscation Structure

The WeAreDevs obfuscator (v1.0.0) generally follows this structure:

1.  **String Table**: A large table (e.g., `local D={...}`) containing encrypted strings.
2.  **Shuffle Loop**: A loop that shuffles the string table based on a seed or algorithm.
3.  **VM / Decryption Loop**: The main code logic is often wrapped in a VM-like structure or uses a custom string decryptor function.
4.  **Environment Checks**: Scripts often check for exploit-specific globals (`getgenv`, `checkcaller`) or Roblox specifics (`game.PlaceId`).
5.  **Payload Execution**: The final payload is often constructed as a string (sometimes byte codes) and executed via `loadstring`.

## Tools Developed

### 1. Dynamic Dumper (`tools/dumper.lua`)

This tool mocks the Lua 5.1 runtime and Roblox environment to intercept obfuscated script behavior.

**Key Features:**
*   **Environment Mocking**: Mocks `game`, `script`, `StarterGui`, `Drawing`, `Vector2`, `Vector3`, `CFrame`, `UDim2`, `Instance`, `Enum`, `task`.
*   **Exploit Globals**: Mocks `getgenv`, `getrenv`, `checkcaller`, `identifyexecutor`.
*   **Interceptor**:
    *   Intercepts `loadstring` to capture and log dynamic payloads.
    *   Intercepts `game.StarterGui:SetCore` notifications.
    *   Intercepts `table.concat` to reveal large string construction (often encrypted payloads).
*   **Robustness**: Implements `__concat`, `__len`, and `__tostring` on proxies to handle string manipulation of mocked objects without crashing.

### 2. Static Extractor (`tools/extract_strings.py`)

A Python script for statically extracting and decrypting strings. Useful for quick analysis but less resilient to obfuscation changes.

### 3. CLI Runner (`tools/run_dumper.py`)

Automates the execution of `dumper.lua` with the system's `lua` interpreter.

## Analysis of Test Cases

### Hard Scripts
The "hard" test cases (e.g., `obfuscated_script-1763795101768.lua`) execute successfully in the mock environment.
*   **Behavior**: They generate notifications ("System bereit", "Lade Module...") and construct large strings of numbers (e.g., `1741501741...`).
*   **Payload**: The numeric strings likely represent the encrypted payload, but `loadstring` is not called on them during the trace. The script might be waiting for user interaction or specific environment triggers not yet mocked.

### Extreme Scripts
The "extreme" test cases (e.g., `obfuscated_script-1763796707374.lua`) are highly sensitive to the environment.
*   **Status**: Currently crashing with "attempt to concatenate local 'Z' (a table value)".
*   **Cause**: The script likely enters a control flow path where a variable (`Z`) is initialized as a table (e.g., `{}`) but later used in a string concatenation. This suggests an anti-tamper check failure or complex VM logic that requires precise return values from mocked functions.

## Future Work

*   **Deep VM Analysis**: The "extreme" crash requires stepping through the obfuscated VM logic to understand why the state becomes inconsistent.
*   **Payload Decryption**: Analyzing the numeric strings from the "hard" scripts to verify if they are indeed bytecode or encrypted source.
