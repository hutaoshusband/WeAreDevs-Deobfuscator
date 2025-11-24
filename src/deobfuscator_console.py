import os
import sys
import subprocess
import tempfile
import shutil
import time
import winsound
import base64

_a1 = base64.b64decode(b'TWFkZSBieQ==').decode()
_a2 = base64.b64decode(b'SFVUQU9TSFVTQkFORA==').decode()
_a3 = lambda: f"{_a1} {_a2}"
_verify_attr = lambda s: _a2.lower() in s.lower()

def beep():
    try:
        winsound.Beep(2000, 50)
    except:
        pass

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def find_lua_executable():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        
    local_lua = os.path.join(base_path, "lua.exe")
    if os.path.exists(local_lua):
        return local_lua
        
    for cmd in ["lua5.1", "lua", "luajit"]:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def _get_credit_line(idx=0):
    parts = [_a1, _a2]
    if not all(parts):
        return None
    return " ".join(parts)

def _display_credits(count=100):
    credit = _get_credit_line()
    if not credit or not _verify_attr(credit):
        return False
    for _ in range(count):
        print(credit)
    return True

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("file: ", end='', flush=True)
    try:
        target_path = input().strip()
    except EOFError:
        return

    if target_path.startswith('"') and target_path.endswith('"'):
        target_path = target_path[1:-1]
        
    if not os.path.exists(target_path):
        print("File not found!")
        time.sleep(3)
        return

    beep()

    lua_exec = find_lua_executable()
    if not lua_exec:
        print("Error: No Lua interpreter found. Please install lua5.1, lua, or luajit, or place lua.exe next to this executable.")
        time.sleep(5)
        return

    beep()

    # Read dumper.lua from resources
    # If running from source (tools/deobfuscator_console.py), dumper.lua is in tools/dumper.lua
    # If running from frozen exe, it should be in sys._MEIPASS/dumper.lua
    
    if getattr(sys, 'frozen', False):
         dumper_path = get_resource_path('dumper.lua')
    else:
         # Assuming script is in tools/
         tools_dir = os.path.dirname(os.path.abspath(__file__))
         dumper_path = os.path.join(tools_dir, 'dumper.lua')

    if not os.path.exists(dumper_path):
         print(f"Error: dumper.lua not found at {dumper_path}")
         time.sleep(5)
         return

    try:
        with open(dumper_path, 'rb') as f:
            template = f.read()
    except Exception as e:
        print(f"Error reading dumper template: {e}")
        time.sleep(3)
        return

    try:
        with open(target_path, 'rb') as f:
            obfuscated_content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        time.sleep(3)
        return

    beep()

    placeholder = b"-- PASTE YOUR OBFUSCATED SCRIPT HERE --"
    
    level = 0
    while True:
        eq = b"=" * level
        start_delim = b"[" + eq + b"["
        end_delim = b"]" + eq + b"]"
        if end_delim not in obfuscated_content:
            break
        level += 1
        
    match_start = template.find(b"local OBFUSCATED_SCRIPT =")
    ph_start = template.find(placeholder)
    
    if match_start == -1 or ph_start == -1:
        print("Internal Error: Template structure corrupted.")
        time.sleep(3)
        return

    if b"]]" not in obfuscated_content:
        final_script = template.replace(placeholder, obfuscated_content)
    else:
        open_bracket_pos = template.rfind(b"[[", 0, ph_start)
        close_bracket_pos = template.find(b"]]", ph_start)
        
        if open_bracket_pos == -1 or close_bracket_pos == -1:
            print("Internal Error: Could not find delimiters in template.")
            time.sleep(3)
            return
            
        part1 = template[:open_bracket_pos]
        part2 = template[close_bracket_pos+2:]
        
        final_script = part1 + start_delim + b"\n" + obfuscated_content + b"\n" + end_delim + part2

    beep()

    with tempfile.NamedTemporaryFile(mode='wb', suffix='.lua', delete=False) as tmp:
        tmp.write(final_script)
        tmp_path = tmp.name
    
    try:
        result = subprocess.run([lua_exec, tmp_path], capture_output=True)
        
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
        
        dumped_lines = []
        for line in stdout.splitlines():
            if "[DUMP]" in line:
                dumped_lines.append(line.replace("[DUMP] ", ""))
        
        if stderr:
             if "Error" in stderr or "stack traceback" in stderr:
                 print(f"Lua Error: {stderr}")
        
        if dumped_lines:
            base, ext = os.path.splitext(target_path)
            output_path = f"{base}_deobfuscated{ext}"
            
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write("\n".join(dumped_lines))
            
            print(f"Saved to {output_path}")
            beep()
        else:
            print("No deobfuscated content found.")
            
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    
    if not _display_credits(100):
        print(_a3())
    
    time.sleep(3)

if __name__ == "__main__":
    main()
