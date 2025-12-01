-- Credits: HUTAOSHUSBAND
-- SECURITY PATCH START
-- SECURITY RESTRICTIONS REMOVED AS PER USER REQUEST
-- Full access to environment is enabled.

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

local function CreatePlayersProxy(path)
    local players = CreateProxy("Players", path)
    local mt = getmetatable(players)
    mt.__index = function(t, k)
        if k == "LocalPlayer" then
            local player = CreateProxy("LocalPlayer", path .. ".LocalPlayer")
            local player_mt = getmetatable(player)
            player_mt.__index = function(pt, pk)
                if pk == "Name" then return "LocalPlayer" end
                if pk == "UserId" then return 1 end
                if pk == "Character" then return CreateProxy("Character", path .. ".LocalPlayer.Character") end
                return CreateProxy(pk, path .. ".LocalPlayer." .. pk)
            end
            return player
        end
        return CreateProxy(k, path .. "." .. k)
    end
    return players
end

local function CreateProxy(name, path)
    local proxy = newproxy(true)
    local meta = getmetatable(proxy)
    
    meta.__index = function(t, k)
        local newPath = path .. "." .. tostring(k)
        
        if name == "game" then
            if k == "PlaceId" then return 123456 end
            if k == "JobId" then return "deadbeef-1234-5678-9abc-def012345678" end
            
            -- Services Direct Access
            if k == "StarterGui" then return CreateProxy("StarterGui", "game.StarterGui") end
            if k == "CoreGui" then return CreateProxy("CoreGui", "game.CoreGui") end
            if k == "Players" then 
                 return CreatePlayersProxy("game.Players")
            end
            
            if k == "HttpService" then
                local http = CreateProxy("HttpService", "game.HttpService")
                local mt = getmetatable(http)
                local old_idx = mt.__index
                mt.__index = function(t, k)
                    if k == "JSONDecode" then return function(self, str) return {} end end
                    if k == "JSONEncode" then return function(self, tbl) return "{}" end end
                    if k == "GenerateGUID" then return function(self) return "dead-beef-1234-5678" end end
                    return old_idx(t, k)
                end
                return http
            end

            if k == "ReplicatedStorage" then return CreateProxy("ReplicatedStorage", "game.ReplicatedStorage") end
            if k == "Lighting" then return CreateProxy("Lighting", "game.Lighting") end
            if k == "TeleportService" then return CreateProxy("TeleportService", "game.TeleportService") end
            if k == "MarketplaceService" then return CreateProxy("MarketplaceService", "game.MarketplaceService") end
            if k == "UserInputService" then return CreateProxy("UserInputService", "game.UserInputService") end

            if k == "HttpGet" or k == "HttpGetAsync" then
                return function(self, url)
                    Log(string.format('game:HttpGet("%s")', tostring(url)))
                    return "KEY_1234_ABC_FAKE_PAYLOAD" -- Dummy return for key systems
                end
            end
            if k == "GetService" then
                 return function(self, serviceName)
                     Log(string.format('game:GetService("%s")', tostring(serviceName)))
                     local svcPath = "game." .. tostring(serviceName)
                     
                     if serviceName == "Players" then
                         return CreatePlayersProxy(svcPath)
                     end

                     if serviceName == "HttpService" then
                        local http = CreateProxy("HttpService", svcPath)
                        local mt = getmetatable(http)
                        local old_idx = mt.__index
                        mt.__index = function(t, k)
                            if k == "JSONDecode" then
                                return function(self, str) return {} end
                            end
                            if k == "JSONEncode" then
                                return function(self, tbl) return "{}" end
                            end
                            if k == "GenerateGUID" then
                                return function(self) return "dead-beef-1234-5678" end
                            end
                            return old_idx(t, k)
                        end
                        return http
                     end

                     if serviceName == "ReplicatedStorage" then return CreateProxy("ReplicatedStorage", svcPath) end
                     if serviceName == "Lighting" then return CreateProxy("Lighting", svcPath) end
                     if serviceName == "CoreGui" then return CreateProxy("CoreGui", svcPath) end
                     if serviceName == "TeleportService" then return CreateProxy("TeleportService", svcPath) end
                     if serviceName == "MarketplaceService" then return CreateProxy("MarketplaceService", svcPath) end
                     if serviceName == "UserInputService" then return CreateProxy("UserInputService", svcPath) end
                     
                     return CreateProxy(serviceName, svcPath)
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
                 
                 local connection = CreateProxy("Connection", newPath .. ":Connect()")
                 local cm = getmetatable(connection)
                 cm.__index = function(ct, ck)
                     if ck == "Disconnect" or ck == "disconnect" then return function() end end
                     return CreateProxy(ck, "Connection." .. ck)
                 end
                 return connection
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
-- Defined later after Vector3 is fixed

local Color3 = MakeStaticLib("Color3")
function Color3.new(r, g, b)
    return MakeSafeObject("Color3", {r=r, g=g, b=b}, {
        __tostring = function(self) return string.format("%f, %f, %f", self.r, self.g, self.b) end
    })
end
function Color3.fromRGB(r, g, b) return Color3.new(r/255, g/255, b/255) end
function Color3.fromHSV(h, s, v) return Color3.new(1,1,1) end

local UDim2 = MakeStaticLib("UDim2")
function UDim2.new(...) 
    return MakeSafeObject("UDim2", {}, {
        __tostring = function() return "{0, 0}, {0, 0}" end
    })
end
function UDim2.fromScale(x, y) return UDim2.new(x, 0, y, 0) end
function UDim2.fromOffset(x, y) return UDim2.new(0, x, 0, y) end

local Vector3 = MakeStaticLib("Vector3")
function Vector3.new(...) 
    -- Removed 'unit=Vector3.new()' to prevent stack overflow
    return MakeSafeObject("Vector3", {x=0,y=0,z=0, magnitude=0}, {
        __tostring = function() return "0, 0, 0" end,
        __add = function() return Vector3.new() end,
        __sub = function() return Vector3.new() end,
        __mul = function() return Vector3.new() end,
        __div = function() return Vector3.new() end
    })
end
function Vector3.fromDate(t) return Vector3.new() end

local Vector2 = MakeStaticLib("Vector2")
function Vector2.new(x, y) 
    -- Removed 'unit=Vector2.new()' to prevent stack overflow
    return MakeSafeObject("Vector2", {x=x or 0, y=y or 0, magnitude=0}, {
        __tostring = function(self) return string.format("Vector2.new(%s, %s)", self.x, self.y) end,
        __add = function() return Vector2.new() end,
        __sub = function() return Vector2.new() end,
        __mul = function() return Vector2.new() end,
        __div = function() return Vector2.new() end
    })
end

-- Now define CFrame properly
function CFrame.new(...)
    return MakeSafeObject("CFrame", {x=0, y=0, z=0, p=Vector3.new(0,0,0), lookVector=Vector3.new(0,0,1)}, {
        __tostring = function() return "0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1" end,
        __add = function() return CFrame.new() end,
        __sub = function() return CFrame.new() end,
        __mul = function() return CFrame.new() end
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
local ClassProperties = {
    Part = { Size = Vector3.new(1,1,1), Position = Vector3.new(0,0,0) },
    Humanoid = { Health = 100, MaxHealth = 100 },
    ScreenGui = { DisplayOrder = 0 },
    Frame = { Size = UDim2.new(0,100,0,100) },
    TextLabel = { Text = "" }
}

function Instance.new(className)
    local path = "Instance.new('" .. className .. "')"
    local proxy = CreateProxy(className, path)
    local props = ClassProperties[className]
    if props then
        local mt = getmetatable(proxy)
        local base_index = mt.__index
        mt.__index = function(t, k)
            if props[k] then return props[k] end
            return base_index(t, k)
        end
    end
    return proxy
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

-- Extended Roblox Types
local TweenInfo = MakeStaticLib("TweenInfo")
function TweenInfo.new(...) return MakeSafeObject("TweenInfo") end

local UDim = MakeStaticLib("UDim")
function UDim.new(...) return MakeSafeObject("UDim") end

local Ray = MakeStaticLib("Ray")
function Ray.new(...) return MakeSafeObject("Ray") end

local BrickColor = MakeStaticLib("BrickColor")
function BrickColor.new(...) return MakeSafeObject("BrickColor") end
function BrickColor.random() return MakeSafeObject("BrickColor") end

local Region3 = MakeStaticLib("Region3")
function Region3.new(...) return MakeSafeObject("Region3") end

-- Crypt Library
local Crypt = MakeStaticLib("crypt")
function Crypt.encrypt(d) return d end
function Crypt.decrypt(d) return d end
function Crypt.hash(d) return "hash" end
function Crypt.generatekey() return "key" end
function Crypt.base64encode(d) return d end
function Crypt.base64decode(d) return d end
Crypt.base64 = {
    encode = function(d) return d end,
    decode = function(d) return d end
}
Crypt.custom = {
    encrypt = function(d) return d end,
    decrypt = function(d) return d end
}

-- Console
local function MockConsole(...) Log("RCONSOLE: " .. tostring(...)) end

setmetatable(MockEnv, {
    __index = function(t, k)
        -- Primary Roblox Services/Globals
        if k == "game" then return CreateProxy("game", "game") end
        if k == "workspace" then return CreateProxy("workspace", "workspace") end
        if k == "script" then return CreateProxy("script", "script") end
        if k == "wait" then return function(n) end end
        if k == "spawn" then return function(f) f() end end
        if k == "delay" then return function(n, f) f() end end
        if k == "print" then return MockPrint end
        if k == "warn" then return MockPrint end
        if k == "error" then return MockPrint end
        
        -- Libraries
        if k == "bit" or k == "bit32" then return Bit32 end
        if k == "CFrame" then return CFrame end
        if k == "Color3" then return Color3 end
        if k == "UDim2" then return UDim2 end
        if k == "UDim" then return UDim end
        if k == "Vector3" then return Vector3 end
        if k == "Vector2" then return Vector2 end
        if k == "Drawing" then return Drawing end
        if k == "Instance" then return Instance end
        if k == "Enum" then return Enum end
        if k == "task" then return task end
        if k == "TweenInfo" then return TweenInfo end
        if k == "Ray" then return Ray end
        if k == "BrickColor" then return BrickColor end
        if k == "Region3" then return Region3 end
        
        -- Standard Lua
        if k == "typeof" then return type end
        if k == "pairs" then return MockPairs end
        if k == "ipairs" then return MockIPairs end
        if k == "newproxy" then 
             -- Log("DEBUG: Accessing newproxy. Value: " .. tostring(newproxy))
             return newproxy 
        end
        if k == "string" then return MockString end
        if k == "table" then return MockTable end
        if k == "loadstring" then return MockLoadstring end
        if k == "load" then return MockLoadstring end
        
        -- Executor Specific
        if k == "setclipboard" or k == "toclipboard" then return function(s) Log("setclipboard: " .. tostring(s)) end end
        if k == "getgenv" then return function() return EnvProxy end end
        if k == "getrenv" then return function() return RealEnv end end
        if k == "checkcaller" then return function() return true end end
        if k == "identifyexecutor" or k == "getexecutorname" then return function() return "Synapse X", "2.0.0" end end
        if k == "getrawmetatable" then return function(t) return getmetatable(t) end end
        if k == "gethui" then return CreateProxy("HUI", "gethui()") end
        if k == "getnilinstances" then return function() return {} end end
        if k == "getinstances" then return function() return {} end end
        if k == "getgc" then return function() return {} end end
        if k == "getreg" then return function() return {} end end
        if k == "getloadedmodules" then return function() return {} end end
        if k == "getconnections" then return function() return {} end end
        if k == "firesignal" then return function() end end
        
        if k == "setreadonly" then return function() end end
        if k == "isreadonly" then return function() return false end end
        if k == "hookfunction" then return function(f, h) return f end end
        if k == "hookmetamethod" then return function(o, m, f) return function() end end end
        if k == "newcclosure" then return function(f) return f end end
        if k == "islclosure" then return function() return false end end
        if k == "iscclosure" then return function() return true end end
        if k == "getsynasset" then return function(p) return "content" end end

        if k == "request" or k == "http_request" or k == "syn" and k.request then return request end
        
        -- Filesystem
        if k == "readfile" then return function(f) Log("readfile: "..tostring(f)); return "" end end
        if k == "writefile" then return function(f, c) Log("writefile: "..tostring(f)); end end
        if k == "appendfile" then return function(f, c) Log("appendfile: "..tostring(f)); end end
        if k == "isfile" then return function() return false end end
        if k == "isfolder" then return function() return false end end
        if k == "makefolder" then return function() end end
        if k == "delfolder" then return function() end end
        if k == "delfile" then return function() end end
        if k == "listfiles" then return function() return {} end end
        
        -- Console
        if k == "rconsoleprint" then return MockConsole end
        if k == "rconsoleinfo" then return MockConsole end
        if k == "rconsolewarn" then return MockConsole end
        if k == "rconsoleerr" then return MockConsole end
        if k == "rconsoleclear" then return function() end end
        if k == "rconsolename" then return function() end end
        
        -- Input
        if k == "mouse1click" then return function() end end
        if k == "mouse1press" then return function() end end
        if k == "mouse1release" then return function() end end
        if k == "keypress" then return function() end end
        if k == "keyrelease" then return function() end end
        if k == "mousemoveabs" then return function() end end
        if k == "mousemoverel" then return function() end end
        if k == "iswindowactive" then return function() return true end end

        if k == "crypt" then return Crypt end
        if k == "syn" then
             return {
                 request = request,
                 crypt = Crypt,
                 queue_on_teleport = function() end,
                 protect_gui = function() end,
                 secure_call = function(f, ...) return f(...) end
             }
        end
        if k == "fluxus" then return MockEnv.syn end
        
        if k == "debug" then
            return {
                getinfo = function() return {source="mock", short_src="mock", func=function() end} end,
                getconstants = function() return {} end,
                getconstant = function() return nil end,
                getupvalues = function() return {} end,
                getupvalue = function() return nil end,
                getprotos = function() return {} end,
                getproto = function() return nil end,
                getstack = function() return {} end,
                setstack = function() end,
                setconstant = function() end,
                setupvalue = function() end,
                getregistry = function() return {} end,
                getmetatable = function(t) return getmetatable(t) end,
                setmetatable = function(t, m) return setmetatable(t, m) end,
                profilebegin = function() end,
                profileend = function() end,
                traceback = function() return "mock traceback" end
            }
        end
        
        -- Fallback to Real Environment for everything else
        -- "lua 5.1 mock everything and make it work please"
        if RealEnv[k] then return RealEnv[k] end
        
        return nil
    end,
    __newindex = function(t, k, v)
        -- Allow setting globals within the mock environment only, not the real one.
        rawset(t, k, v)
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
    -- Enable a hook to detect infinite loops or long running execution
    local start_time = os.clock and os.clock() or 0
    debug.sethook(function()
        if os.clock and (os.clock() - start_time) > 5 then
            error("Timeout: Script execution exceeded 5 seconds")
        end
    end, "l", 100000)

    local status, result = pcall(func)
    debug.sethook() -- Remove hook
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
