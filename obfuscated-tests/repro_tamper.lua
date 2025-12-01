
-- Reproduction of common anti-tamper and nil value issues

local function assert_val(name, val, expected)
    if val ~= expected then
        print("FAIL: " .. name .. " expected " .. tostring(expected) .. " but got " .. tostring(val))
    else
        print("PASS: " .. name)
    end
end

local function assert_exists(name, val)
    if val == nil then
        print("FAIL: " .. name .. " is nil")
    else
        print("PASS: " .. name .. " exists")
    end
end

print("Starting tamper checks...")

-- 1. Check getgenv integrity
local genv = getgenv()
assert_exists("getgenv()", genv)
if genv then
    genv.TestVar = 123
    assert_val("getgenv().TestVar", genv.TestVar, 123)
end

-- 2. Check game properties
assert_exists("game", game)
if game then
    assert_exists("game.PlaceId", game.PlaceId)
    assert_exists("game.JobId", game.JobId)
    print("game.PlaceId type: " .. type(game.PlaceId))
    -- Some scripts expect PlaceId to be a number
end

-- 3. Check LocalPlayer
local lp = game:GetService("Players").LocalPlayer
assert_exists("LocalPlayer", lp)
if lp then
    assert_exists("LocalPlayer.Name", lp.Name)
    assert_exists("LocalPlayer.UserId", lp.UserId)
    -- assert_exists("LocalPlayer.Character", lp.Character) -- Character might be nil initially in real game, but scripts often wait for it
end

-- 4. Check crypto/bit libraries
if bit then
    assert_val("bit.band(1, 0)", bit.band(1, 0), 0)
    assert_val("bit.bor(1, 0)", bit.bor(1, 0), 1)
else
    print("FAIL: bit library missing")
end

-- 5. Check anti-tamper: iscclosure on game methods
if iscclosure then
    -- game.GetService should be a C closure (or mimic one)
    local is_cc = iscclosure(game.GetService)
    print("iscclosure(game.GetService): " .. tostring(is_cc))
    -- If we mock it as a lua function, iscclosure will return false (or true if we lie)
    -- If the script checks this and expects true (because it's a Roblox function), we might fail if we return false.
end

-- 6. Check Metatable tampering
local mt = getrawmetatable(game)
assert_exists("getrawmetatable(game)", mt)
if mt then
    if isreadonly then
       print("isreadonly(mt): " .. tostring(isreadonly(mt)))
    end
end

-- 7. Check for nil values on common services
local rs = game:GetService("ReplicatedStorage")
assert_exists("ReplicatedStorage", rs)
local uis = game:GetService("UserInputService")
assert_exists("UserInputService", uis)

-- 8. Check for nil values on newproxy/userdata
local p = newproxy(true)
if type(p) ~= "userdata" then
    print("FAIL: newproxy did not return userdata, got " .. type(p))
end

-- 9. Check debug.getinfo
if debug and debug.getinfo then
    local info = debug.getinfo(print)
    assert_exists("debug.getinfo(print)", info)
end

-- 10. Check "Tamper Detected" scenarios
-- e.g., accessing a property that shouldn't error but returns nil?
-- Or accessing a property that triggers a detection?

print("Tamper checks complete.")
