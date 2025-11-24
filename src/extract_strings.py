import re
import sys
import os

def solve_expr(expr):
    try:
        return eval(expr)
    except Exception as e:
        return 0

def decode_lua_string(s):
    def repl(m):
        if m.group(1): return chr(int(m.group(1)))
        return m.group(0)
    s = re.sub(r'\\(\d{1,3})', repl, s)
    escapes = {
        r'\n': '\n', r'\r': '\r', r'\t': '\t', r'\\': '\\', r'\"': '"', r"\'": "'", r'\0': '\0'
    }
    for k, v in escapes.items():
        s = s.replace(k, v)
    return s

def extract_strings_from_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='latin1') as f:
        content = f.read()

    match_func = re.search(r'return\s*\(\s*function\s*\(\s*\.\.\.\s*\)', content)
    if not match_func:
        print("  Not a standard WeAreDevs obfuscated script (missing outer wrapper)")
        return

    start_idx = match_func.end()
    search_area = content[start_idx:start_idx+2000]

    match_table_def = re.search(r'local\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', search_area)
    if not match_table_def:
        print("  Could not find string table definition")
        return

    table_var = match_table_def.group(1)
    print(f"  Table variable: {table_var}")

    table_start_idx = content.find('{', start_idx) + 1
    
    strings = []
    pos = table_start_idx
    
    while pos < len(content):
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content): break
        
        if content[pos] == '}':
            break
            
        if content[pos] == '"' or content[pos] == "'":
            quote = content[pos]
            end_quote = pos + 1
            while end_quote < len(content):
                if content[end_quote] == quote and content[end_quote-1] != '\\':
                    break
                if content[end_quote] == quote and content[end_quote-1] == '\\':
                     bk = 1
                     while content[end_quote - 1 - bk] == '\\':
                         bk += 1
                     if bk % 2 == 0:
                         pass
                     else:
                         break
                end_quote += 1
            
            str_content = content[pos+1:end_quote]
            strings.append(decode_lua_string(str_content))
            pos = end_quote + 1
            
            while pos < len(content) and (content[pos].isspace() or content[pos] in ',;'):
                pos += 1
        else:
            pos += 1

    print(f"  Found {len(strings)} encoded strings.")

    match_shuffle = re.search(r'for\s+([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s+in\s+ipairs\s*\(\s*\{(.*?)\}\s*\)\s*do', content, re.DOTALL)
    if not match_shuffle:
        print("  Could not find shuffle loop")
        return

    shuffle_content = match_shuffle.group(3)
    
    pairs = []
    for m in re.finditer(r'\{([^}]+)\}', shuffle_content):
        pair_str = m.group(1)
        parts = re.split(r'[;,]', pair_str)
        if len(parts) >= 2:
            s_val = solve_expr(parts[0])
            e_val = solve_expr(parts[1])
            pairs.append((s_val, e_val))
            
    for start, end in pairs:
        s = start - 1
        e = end - 1
        while s < e:
            if s < len(strings) and e < len(strings):
                strings[s], strings[e] = strings[e], strings[s]
            s += 1
            e -= 1

    pattern_accessor = r'local\s+function\s+([a-zA-Z0-9_]+)\s*\([a-zA-Z0-9_]+\)\s*return\s+' + re.escape(table_var) + r'\[[a-zA-Z0-9_]+\s*([+\-])\s*\((.*?)\)\]\s*end'
    match_acc = re.search(pattern_accessor, content)
    
    offset = 0
    if match_acc:
        sign = match_acc.group(2)
        expr = match_acc.group(3)
        val = solve_expr(expr)
        if sign == '-':
            offset = val
        else:
            offset = -val
    else:
        print("  Could not find accessor function offset. Assuming 0.")
    
    match_do = re.search(r'do\s+local\s+[a-zA-Z0-9_]+\s*=\s*table\.concat', content)
    if not match_do:
        match_do = re.search(r'do\s+local\s+[a-zA-Z0-9_]+\s*=\s*string\.len', content)
        
    if match_do:
        start_do = match_do.start()
        search_area_do = content[start_do:start_do+5000]
        
        match_map = re.search(r'local\s+([a-zA-Z0-9_]+)\s*=\s*\{', search_area_do)
        if match_map:
             map_var = match_map.group(1)
             map_start = search_area_do.find('{', match_map.end() - 1) + 1
             cnt = 1
             map_end = map_start
             while map_end < len(search_area_do) and cnt > 0:
                 if search_area_do[map_end] == '{': cnt += 1
                 if search_area_do[map_end] == '}': cnt -= 1
                 map_end += 1
             map_content = search_area_do[map_start:map_end-1]
             
             base64_map = {}
             
             pos = 0
             while pos < len(map_content):
                while pos < len(map_content) and map_content[pos].isspace(): pos += 1
                if pos >= len(map_content): break
                
                key = None
                if map_content[pos] == '[':
                    end_bracket = map_content.find(']', pos)
                    if end_bracket == -1: break
                    key_str = map_content[pos+1:end_bracket].strip('"')
                    key = decode_lua_string(key_str)
                    pos = end_bracket + 1
                else:
                    match_k = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)', map_content[pos:])
                    if match_k:
                        key = match_k.group(1)
                        pos += len(key)
                    else:
                        pos += 1
                        continue
                
                while pos < len(map_content) and (map_content[pos].isspace() or map_content[pos] == '='):
                    pos += 1
                
                end_val = pos
                while end_val < len(map_content) and map_content[end_val] not in ',;}':
                    end_val += 1
                
                val_expr = map_content[pos:end_val]
                val = solve_expr(val_expr)
                base64_map[key] = val
                pos = end_val + 1
             
             if len(base64_map) > 10:
                 decoded_strings = []
                 for s_enc in strings:
                     if not s_enc or not isinstance(s_enc, str):
                         decoded_strings.append("")
                         continue
                     
                     res_bytes = bytearray()
                     a = 0
                     s = 0
                     for char in s_enc:
                         if char in base64_map:
                             val = base64_map[char]
                             a += val * (64**(3-s))
                             s += 1
                             if s == 4:
                                 b1 = (a >> 16) & 0xFF
                                 b2 = (a >> 8) & 0xFF
                                 b3 = a & 0xFF
                                 res_bytes.append(b1)
                                 res_bytes.append(b2)
                                 res_bytes.append(b3)
                                 a = 0
                                 s = 0
                         elif char == '=':
                             b1 = (a >> 16) & 0xFF
                             res_bytes.append(b1)
                             if s == 3:
                                 b2 = (a >> 8) & 0xFF
                                 res_bytes.append(b2)
                             break
                     
                     try:
                         decoded = res_bytes.decode('utf-8', errors='replace')
                         decoded_strings.append(decoded)
                     except:
                         decoded_strings.append("<binary>")
                 
                 print("  Decrypted strings:")
                 for i, ds in enumerate(decoded_strings):
                     if len(ds) > 3 and all(c.isprintable() for c in ds):
                         print(f"    [{i}] {ds}")
                     elif ds in ["game", "StarterGui", "SetCore", "Info", "Title", "Text", "Duration", "SendNotification"]:
                         print(f"    [{i}] {ds}")

             else:
                 print("  Failed to parse base64 map or map is too small")

def process_path(path):
    if os.path.isfile(path):
        extract_strings_from_file(path)
    elif os.path.isdir(path):
        for fname in os.listdir(path):
            if fname.endswith(".lua"):
                extract_strings_from_file(os.path.join(path, fname))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_path(sys.argv[1])
    else:
        print("Usage: python3 extract_strings.py <path>")
