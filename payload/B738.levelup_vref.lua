-- Zibo / LevelUp VREF, v0.1.0-preview.2. Simulator use only.
-- INTENTIONAL FIX against .35: source-backed landing reference speeds.
-- FCOM PI.10.4 / PI.20.6 / PI.40.4 / PI.50.4 / PI.70.4.
-- Local tables avoid XLua global-table registration and cross-script state.
local tables = {
    [0] = { -- 737-800; table weight in 1000 kg
        kg = true,
        weight = { 40, 45, 50, 55, 60, 65, 70, 75, 80, 85 },
        f15 = { 121, 128, 136, 143, 149, 156, 161, 167, 172, 177 },
        f30 = { 115, 122, 129, 136, 142, 148, 153, 158, 163, 168 },
        f40 = { 108, 115, 122, 128, 135, 141, 146, 151, 155, 160 },
    },
    [1] = { -- 737-900; table weight in 1000 lb
        kg = false,
        weight = { 90, 100, 110, 120, 130, 140, 150, 160, 170, 180 },
        f15 = { 127, 134, 140, 147, 153, 159, 161, 166, 171, 177 },
        f30 = { 119, 126, 132, 138, 144, 149, 151, 156, 161, 166 },
        f40 = { 111, 117, 123, 129, 134, 139, 141, 146, 151, 155 },
    },
    [2] = { -- 737-700; table weight in 1000 lb
        kg = false,
        weight = { 90, 100, 110, 120, 130, 140, 150, 160, 170 },
        f15 = { 115, 121, 127, 133, 139, 145, 150, 155, 159 },
        f30 = { 111, 117, 123, 129, 134, 140, 144, 149, 153 },
        f40 = { 108, 114, 120, 126, 132, 137, 142, 147, 151 },
    },
    [3] = { -- 737-600; table weight in 1000 kg
        kg = true,
        weight = { 38, 42, 46, 50, 54, 58, 62, 66, 70 },
        f15 = { 111, 117, 122, 128, 133, 138, 143, 147, 152 },
        f30 = { 106, 112, 117, 122, 127, 132, 137, 141, 146 },
        f40 = { 104, 110, 115, 120, 125, 130, 135, 139, 144 },
    },
    [4] = { -- 737-900ER; table weight in 1000 lb
        kg = false,
        weight = { 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190 },
        f15 = { 117, 124, 130, 136, 142, 147, 152, 158, 162, 167, 172 },
        f30 = { 112, 118, 124, 130, 135, 140, 145, 150, 154, 158, 162 },
        f40 = { 106, 112, 119, 124, 130, 136, 141, 145, 150, 155, 159 },
    },
}
local KGS_LBS = 2.204622622 -- same conversion as upstream .35
local function finite(value)
    return type(value) == "number" and value == value and value > -math.huge and value < math.huge
end
local function supported(variant)
    return finite(variant) and variant == math.floor(variant)
        and (variant == -1 or tables[variant] ~= nil)
end
local function calculate(weight_klb, variant)
    if not supported(variant) or not finite(weight_klb) or weight_klb <= 0 then
        return nil
    end
    -- Native Zibo is -1; it uses the same FCOM -800 reference as LevelUp ID0.
    -- Other negative/unknown IDs retain upstream behavior through the caller.
    local model = tables[variant == -1 and 0 or variant]
    local weight = model.kg and weight_klb / KGS_LBS or weight_klb
    local count = #model.weight
    weight = math.max(model.weight[1], math.min(model.weight[count], weight))
    local low, high = 1, 1
    for index = 2, count do
        if weight <= model.weight[index] then
            low, high = index - 1, index
            break
        end
    end
    local fraction = 0
    if high ~= low then
        fraction = (weight - model.weight[low]) / (model.weight[high] - model.weight[low])
    end
    local function interpolate(row)
        return row[low] + (row[high] - row[low]) * fraction
    end
    return interpolate(model.f30), interpolate(model.f40), interpolate(model.f15)
end
return { calculate = calculate, supported = supported, version = "v0.1.0-preview.2" }
