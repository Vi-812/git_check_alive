async def final_json_preparation(resp_json):
    code = resp_json.meta.code
    if code == 200:
        pass
    else:
        resp_json.__delattr__('data')
        resp_json.__delattr__('analytic')
    return resp_json.json(by_alias=True), code
