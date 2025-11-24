-- Credits: HUTAOSHUSBAND
local OBFUSCATED_SCRIPT = [[
-- PASTE YOUR OBFUSCATED SCRIPT HERE --
]]

local LOG_CALLS = true

local RealEnv = getfenv()
local MockEnv = {}

local function Log(msg)
    for line in string.gmatch(msg, "[^\r\n]+") do
        print("[DUMP] " .. line)
    end
end

local function FormatValue(val, depth)
    depth = depth or 0
    if depth > 2 then return "..." end
    if type(val) == "string" then
        return string.format("%q", val)
    elseif type(val) == "table" then
        return "{...}"
    elseif type(val) == "function" then
        return "function()"
    else
        return tostring(val)
    end
end

-- Global registry for connections to allow inspection/triggering
local ConnectionRegistry = {}

local function CreateProxy(name, path)
    local proxy = newproxy(true)
    local meta = getmetatable(proxy)
    
    meta.__index = function(t, k)
        local newPath = path .. "." .. tostring(k)
        
        if name == "game" then
            if k == "PlaceId" then return 123456 end
            if k == "JobId" then return "deadbeef-1234-5678-9abc-def012345678" end
            if k == "StarterGui" then
                return CreateProxy("StarterGui", "game.StarterGui")
            end
            if k == "HttpGet" or k == "HttpGetAsync" then
                return function(self, url)
                    Log(string.format('game:HttpGet("%s")', tostring(url)))
                    return "KEY_1234_ABC_FAKE_PAYLOAD" -- Dummy return for key systems
                end
            end
            if k == "GetService" then
                 return function(self, serviceName)
                     Log(string.format('game:GetService("%s")', tostring(serviceName)))
                     return CreateProxy(serviceName, "game." .. tostring(serviceName))
                 end
            end
        end
        
        if k == "SetCore" then
            return function(self, method, args)
                if method == "SendNotification" then
                    local argsStr = "{"
                    if type(args) == "table" then
                        for ak, av in pairs(args) do
                            local valStr = tostring(av)
                            if type(av) == "string" then valStr = string.format("%q", av) end
                            argsStr = argsStr .. "\n    " .. tostring(ak) .. " = " .. valStr .. ";"
                        end
                    end
                    argsStr = argsStr .. "\n}"
                    Log(string.format('game.StarterGui:SetCore("SendNotification", %s)', argsStr))
                else
                    Log(string.format('%s:SetCore(%s, ...)', path, FormatValue(method)))
                end
            end
        end
        
        if k == "Connect" or k == "connect" then 
             return function(self, callback)
                 Log(string.format("Connect called on %s", path))
                 table.insert(ConnectionRegistry, {path=path, callback=callback})
                 
                 -- Heuristic: If it looks like a button click, try to execute it
                 if string.find(path, "Button") or string.find(path, "Click") or string.find(path, "Submit") then
                     Log("  -> Auto-triggering potential button callback...")
                     if type(callback) == "function" then
                         -- Wrap in pcall to prevent crash if callback fails
                         local s, e = pcall(callback)
                         if not s then
                             Log("  -> Callback failed: " .. tostring(e))
                         else
                             Log("  -> Callback executed successfully.")
                         end
                     end
                 end
                 
                 return CreateProxy("Connection", newPath .. ":Connect()")
             end
        end
        
        if RealEnv[k] then return RealEnv[k] end
        return CreateProxy(k, newPath)
    end
    
    meta.__newindex = function(t, k, v)
        if k == "Text" then
             Log(string.format('%s.Text = %s', path, FormatValue(v)))
        end
    end
    
    meta.__call = function(t, ...)
        return CreateProxy("Result", path .. "()")
    end
    
    meta.__concat = function(a, b)
        return tostring(a) .. tostring(b)
    end
    
    meta.__len = function(t)
        return #tostring(t)
    end

    meta.__tostring = function() return name end
    return proxy
end

local function MakeSafeObject(name, props, metafuncs)
    local obj = props or {}
    local mt = metafuncs or {}
    mt.__index = mt.__index or obj
    
    -- Ensure concat works for Lua 5.1
    if mt.__tostring and not mt.__concat then
        mt.__concat = function(a, b) return tostring(a) .. tostring(b) end
    end
    
    setmetatable(obj, mt)
    return obj
end

-- Helper to make static libraries safe (concatable)
local function MakeStaticLib(name, lib)
    lib = lib or {}
    local mt = {
        __tostring = function() return name end,
        __concat = function(a, b) return tostring(a) .. tostring(b) end
    }
    setmetatable(lib, mt)
    return lib
end

local CFrame = MakeStaticLib("CFrame")
function CFrame.new(...)
    return MakeSafeObject("CFrame", {x=0, y=0, z=0}, {
        __tostring = function() return "0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1" end,
        __add = function() return CFrame.new() end,
        __sub = function() return CFrame.new() end,
        __mul = function() return CFrame.new() end
    })
end

local Color3 = MakeStaticLib("Color3")
function Color3.new(r, g, b)
    return MakeSafeObject("Color3", {r=r, g=g, b=b}, {
        __tostring = function(self) return string.format("%f, %f, %f", self.r, self.g, self.b) end
    })
end
function Color3.fromRGB(r, g, b) return Color3.new(r/255, g/255, b/255) end

local UDim2 = MakeStaticLib("UDim2")
function UDim2.new(...) 
    return MakeSafeObject("UDim2", {}, {
        __tostring = function() return "{0, 0}, {0, 0}" end
    })
end

local Vector3 = MakeStaticLib("Vector3")
function Vector3.new(...) 
    return MakeSafeObject("Vector3", {x=0,y=0,z=0}, {
        __tostring = function() return "0, 0, 0" end
    })
end

local Vector2 = MakeStaticLib("Vector2")
function Vector2.new(x, y) 
    return MakeSafeObject("Vector2", {x=x or 0, y=y or 0}, {
        __tostring = function(self) return string.format("Vector2.new(%s, %s)", self.x, self.y) end
    })
end

local Drawing = MakeStaticLib("Drawing")
local DrawingObject = {}
DrawingObject.__index = DrawingObject
function Drawing.new(type)
    local obj = {Visible = false, Type = type, Transparency = 1, Color = Color3.new(1,1,1), Thickness = 1}
    return MakeSafeObject("Drawing", obj, {
        __tostring = function() return "Drawing" end
    })
end

local Instance = MakeStaticLib("Instance")
function Instance.new(className)
    return CreateProxy(className, "Instance.new('" .. className .. "')")
end

local Enum = newproxy(true)
getmetatable(Enum).__index = function(t, k)
    return CreateProxy("Enum." .. k, "Enum." .. k)
end
getmetatable(Enum).__tostring = function() return "Enum" end
getmetatable(Enum).__concat = function(a, b) return tostring(a) .. tostring(b) end

local task = MakeStaticLib("task")
function task.wait(n) end
function task.spawn(f, ...) if f then f(...) end end
function task.defer(f, ...) if f then f(...) end end
function task.delay(t, f, ...) if f then f(...) end end

-- Pure Lua Bitwise Implementation for Lua 5.1
local Bit32 = MakeStaticLib("bit32")

local function to_bits(n)
    n = math.floor(n)
    local bits = {}
    for i = 1, 32 do
        local r = n % 2
        bits[i] = r
        n = (n - r) / 2
    end
    return bits
end

local function from_bits(bits)
    local n = 0
    local p = 1
    for i = 1, 32 do
        if bits[i] == 1 then n = n + p end
        p = p * 2
    end
    return n
end

function Bit32.band(...)
    local args = {...}
    if #args == 0 then return 4294967295 end
    
    local arg_bits = {}
    for i, arg in ipairs(args) do
        arg_bits[i] = to_bits(arg)
    end

    local res_bits = {}
    for i = 1, 32 do
        local bit = 1
        for j = 1, #args do
            if arg_bits[j][i] == 0 then
                bit = 0
                break
            end
        end
        res_bits[i] = bit
    end
    return from_bits(res_bits)
end

function Bit32.bor(...)
    local args = {...}
    if #args == 0 then return 0 end
    
    local arg_bits = {}
    for i, arg in ipairs(args) do
        arg_bits[i] = to_bits(arg)
    end

    local res_bits = {}
    for i = 1, 32 do
        local bit = 0
        for j = 1, #args do
            if arg_bits[j][i] == 1 then
                bit = 1
                break
            end
        end
        res_bits[i] = bit
    end
    return from_bits(res_bits)
end

function Bit32.bxor(...)
    local args = {...}
    if #args == 0 then return 0 end
    
    local arg_bits = {}
    for i, arg in ipairs(args) do
        arg_bits[i] = to_bits(arg)
    end

    local res_bits = {}
    for i = 1, 32 do
        local bit = 0
        for j = 1, #args do
             if arg_bits[j][i] == 1 then
                 bit = (bit == 0) and 1 or 0
             end
        end
        res_bits[i] = bit
    end
    return from_bits(res_bits)
end

function Bit32.bnot(a)
    local ba = to_bits(a)
    local res = {}
    for i = 1, 32 do res[i] = (ba[i] == 0) and 1 or 0 end
    return from_bits(res)
end

function Bit32.lshift(a, b)
    return (math.floor(a) * (2 ^ math.floor(b))) % (2 ^ 32)
end

function Bit32.rshift(a, b)
    return math.floor(math.floor(a) / (2 ^ math.floor(b)))
end

-- Aliases
Bit32.arshift = Bit32.rshift

local function MockNext(t, k)
    if type(t) == "userdata" then return nil end
    return next(t, k)
end

local function MockPairs(t)
    if type(t) == "userdata" then return function() return nil end end
    return pairs(t)
end

local function MockIPairs(t)
    if type(t) == "userdata" then return function() return nil end end
    return ipairs(t)
end

local function MockPrint(...)
    local args = {...}
    local str = ""
    for i, v in ipairs(args) do
        str = str .. tostring(v) .. (i < #args and "\t" or "")
    end
    Log("PRINT: " .. str)
end

-- Mock Loadstring
local function MockLoadstring(str, chunkname)
    Log("LOADSTRING DETECTED (len=" .. string.len(str) .. ")")
    if string.len(str) > 0 then
         local snippet = string.sub(str, 1, 500)
         if string.len(str) > 500 then snippet = snippet .. "..." end
         Log("LOADSTRING CONTENT: " .. snippet)
    end
    
    local func, err = loadstring(str, chunkname)
    if func then
        setfenv(func, MockEnv) -- Ensure the loaded chunk uses our mock env
    end
    return func, err
end

-- Mock String Library
local MockString = MakeStaticLib("string", {})
for k, v in pairs(string) do MockString[k] = v end
function MockString.char(...)
    local res = string.char(...)
    return res
end

-- Mock Table Library
local MockTable = MakeStaticLib("table", {})
for k, v in pairs(table) do MockTable[k] = v end
function MockTable.concat(t, sep, i, j)
    local res = table.concat(t, sep, i, j)
    if type(res) == "string" then
        if string.len(res) > 100 then
             Log("TABLE.CONCAT LARGE STRING (len="..string.len(res)..")")
             local snippet = string.sub(res, 1, 500)
             if string.len(res) > 500 then snippet = snippet .. "..." end
             Log("TABLE.CONCAT CONTENT: " .. snippet)
        end
    end
    return res
end

if not math.clamp then math.clamp = function(x, min, max) return x < min and min or (x > max and max or x) end end

-- Env Proxy to handle 'getgenv' returning a concatable/indexable object that writes to MockEnv
local EnvProxy = newproxy(true)
local EnvMt = getmetatable(EnvProxy)
EnvMt.__index = function(t, k) return MockEnv[k] end
EnvMt.__newindex = function(t, k, v) MockEnv[k] = v end
EnvMt.__tostring = function() return "EnvProxy" end
EnvMt.__concat = function(a, b) return tostring(a) .. tostring(b) end

-- Additional global mocks
local function request(options)
    Log("request/http_request called with url: " .. tostring(options.Url))
    return {
        StatusCode = 200,
        Body = "KEY_1234_ABC_FAKE_PAYLOAD",
        Headers = {}
    }
end

setmetatable(MockEnv, {
    __index = function(t, k)
        if k == "game" then return CreateProxy("game", "game") end
        if k == "workspace" then return CreateProxy("workspace", "workspace") end
        if k == "script" then return CreateProxy("script", "script") end
        if k == "wait" then return function(n) end end
        if k == "spawn" then return function(f) f() end end
        if k == "delay" then return function(n, f) f() end end
        if k == "print" then return MockPrint end
        if k == "warn" then return MockPrint end
        if k == "bit" or k == "bit32" then return Bit32 end
        if k == "CFrame" then return CFrame end
        if k == "Color3" then return Color3 end
        if k == "UDim2" then return UDim2 end
        if k == "Vector3" then return Vector3 end
        if k == "Vector2" then return Vector2 end
        if k == "Drawing" then return Drawing end
        if k == "Instance" then return Instance end
        if k == "Enum" then return Enum end
        if k == "task" then return task end
        if k == "typeof" then return type end
        if k == "pairs" then return MockPairs end
        if k == "ipairs" then return MockIPairs end
        if k == "next" then return MockNext end
        if k == "string" then return MockString end
        if k == "table" then return MockTable end
        if k == "loadstring" then return MockLoadstring end
        if k == "load" then return MockLoadstring end
        if k == "setclipboard" then return function(s) Log("setclipboard: " .. tostring(s)) end end
        
        if k == "getgenv" then return function() return EnvProxy end end
        if k == "getrenv" then return function() return RealEnv end end
        if k == "checkcaller" then return function() return true end end
        if k == "identifyexecutor" or k == "getexecutorname" then return function() return "Synapse X", "2.0.0" end end
        
        if k == "request" or k == "http_request" then return request end

        if RealEnv[k] then return RealEnv[k] end
        return nil
    end,
    __newindex = function(t, k, v)
        RealEnv[k] = v
    end
})

if not newproxy then
    function newproxy(u)
        local t = {}
        if u then
            local mt = {}
            setmetatable(t, mt)
        end
        return t
    end
end

local func, err = loadstring(OBFUSCATED_SCRIPT)
if func then
    setfenv(func, MockEnv)
    Log("Executing script...")
    local status, result = pcall(func)
    if status then
         Log("Script finished successfully")
         if result then
             Log("RETURN TYPE: " .. type(result))
             if type(result) == "string" then
                 Log("RETURN LEN: " .. string.len(result))
                 Log("RETURN VAL: " .. result)
             else
                 Log("RETURN VAL: " .. tostring(result))
             end
         else
             Log("RETURN VAL: nil")
         end
    else
        Log("Error running script: " .. tostring(result))
    end
else
    Log("Failed to load script: " .. tostring(err))
end
