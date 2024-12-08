local cjson = require("cjson")

-- Transform request
ngx.req.read_body()
local body = ngx.req.get_body_data()
local method = ngx.req.get_method()

if body then
    local success, json = pcall(cjson.decode, body)
    if success and json.query then
        ngx.req.set_body_data(json.query)
    end
end

-- Transform response
local function transform_response(response)
    local success, json = pcall(cjson.decode, response)
    if not success then
        return response
    end

    if json.results and json.results.bindings then
        local transformed = {}
        for _, binding in ipairs(json.results.bindings) do
            local result = {}
            for var, value in pairs(binding) do
                result[var] = value.value
            end
            table.insert(transformed, result)
        end
        return cjson.encode(transformed)
    end
    return response
end

-- Map HTTP methods to ngx constants
local method_map = {
    GET = ngx.HTTP_GET,
    POST = ngx.HTTP_POST,
    PUT = ngx.HTTP_PUT,
    DELETE = ngx.HTTP_DELETE,
    OPTIONS = ngx.HTTP_OPTIONS
}

-- Capture and transform the response
local capture = ngx.location.capture("/query" .. (ngx.var.is_args or "") .. (ngx.var.args or ""), {
    method = method_map[method] or ngx.HTTP_GET,
    body = ngx.req.get_body_data(),
    always_forward_body = true
})

if capture.status == 200 then
    ngx.status = capture.status
    ngx.header["Content-Type"] = "application/json"
    ngx.say(transform_response(capture.body))
else
    ngx.status = capture.status
    ngx.say(capture.body)
end
