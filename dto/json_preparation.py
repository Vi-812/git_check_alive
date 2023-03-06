async def final_json_preparation(rec_request, resp_json):
    code = resp_json.meta.code
    if code == 200:
        resp_json.__delattr__('error')
        if rec_request.response_type == 'repo':
            resp_json.data.__delattr__('bug_issues_count')
            resp_json.data.__delattr__('bug_issues_closed_count')
            resp_json.data.__delattr__('bug_issues_open_count')
            resp_json.data.__delattr__('bug_issues_no_comment')
            resp_json.data.__delattr__('bug_issues_closed2m')
            resp_json.data.__delattr__('closed_bug_95perc')
            resp_json.data.__delattr__('closed_bug_50perc')
    else:
        resp_json.__delattr__('data')
    return resp_json.json(by_alias=True), code
