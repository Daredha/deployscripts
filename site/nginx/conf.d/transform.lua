local cjson = require("cjson")

-- Transform request
ngx.req.read_body()
local body = ngx.req.get_body_data()

if body then
    local success, json = pcall(cjson.decode, body)
    if success and json.query then
        -- Set the required headers for Oxigraph
        ngx.req.set_header("Content-Type", "application/sparql-query")
        ngx.req.set_header("Accept", "application/sparql-results+json")
        -- Set the raw SPARQL query as the body
        ngx.req.set_body_data(json.query)
    end
end

-- Make the subrequest to the internal location
local res = ngx.location.capture("/query", {
    method = ngx.HTTP_POST,
    body = ngx.req.get_body_data(),
    always_forward_body = true
})

if res.status == 200 then
    ngx.status = res.status
    ngx.header["Content-Type"] = "application/json"
    ngx.print(res.body)
else
    ngx.status = res.status
    ngx.header["Content-Type"] = "application/json"
    ngx.say('{"error": "Failed to execute SPARQL query", "status": ' .. res.status .. '}')
end

-- Exit to prevent further processing
ngx.exit(ngx.OK)
