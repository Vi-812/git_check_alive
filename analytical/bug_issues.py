from statistics import median
from datetime import datetime
import analytical.func_api_client as fa


class BugIssuesAnalytic():
    def __init__(self):
        self.bug_issues_closed_total_count = 0
        self.bug_issues_open_total_count = 0
        self.bug_issues_no_comment = 0
        self.bug_issues_duration_closed_list = []
        self.bug_issues_duration_open_list = []

    def push_bug_issues(self, data):
        now_time = datetime.now()
        for bug_issue in data:
            created_at = fa.to_date(bug_issue['node']['createdAt'])
            comment_count = bug_issue['node']['comments']['totalCount']
            if bug_issue['node']['comments']['nodes']:
                last_comment = bug_issue['node']['comments']['nodes'][0]['createdAt']
            else:
                last_comment = None

            if bug_issue['node']['closed']:
                closed_at = fa.to_date(bug_issue['node']['closedAt'])
                self.bug_issues_closed_total_count += 1
                self.bug_issues_duration_closed_list.append(closed_at - created_at)
            else:
                self.bug_issues_open_total_count += 1
                self.bug_issues_duration_open_list.append(now_time - created_at)
            if not comment_count:
                self.bug_issues_no_comment += 1

    def get_bug_analytic(self):
        closed_list_len = len(self.bug_issues_duration_closed_list)
        open_list_len = len(self.bug_issues_duration_open_list)
        if closed_list_len >= 10:
            bug_issues_closed_two_months = 0
            self.bug_issues_duration_closed_list.sort()
            self.duration_closed_bug_min = self.bug_issues_duration_closed_list[0]
            self.duration_closed_bug_max = self.bug_issues_duration_closed_list[-1]
            self.duration_closed_bug_95percent = self.bug_issues_duration_closed_list[round((closed_list_len - 1)
                                                                                            * 0.95)].days
            self.duration_closed_bug_50percent = median(self.bug_issues_duration_closed_list).days
            for i in range(closed_list_len):
                if self.bug_issues_duration_closed_list[i].days < 60:
                    bug_issues_closed_two_months += 1
                else:
                    break
        else:
            self.duration_closed_bug_min = None
            self.duration_closed_bug_max = None
            self.duration_closed_bug_95percent = None
            self.duration_closed_bug_50percent = None
            bug_issues_closed_two_months = None

        if open_list_len >= 10:
            self.bug_issues_duration_open_list.sort()
            self.duration_open_bug_min = self.bug_issues_duration_open_list[0]
            self.duration_open_bug_max = self.bug_issues_duration_open_list[-1]
            self.duration_open_bug_50percent = median(self.bug_issues_duration_open_list).days
        else:
            self.duration_open_bug_min = None
            self.duration_open_bug_max = None
            self.duration_open_bug_50percent = None
        return [
            self.bug_issues_closed_total_count,
            self.bug_issues_open_total_count,
            self.bug_issues_no_comment,
            self.duration_closed_bug_min,
            self.duration_closed_bug_max,
            self.duration_closed_bug_95percent,
            self.duration_closed_bug_50percent,
            self.duration_open_bug_min,
            self.duration_open_bug_max,
            self.duration_open_bug_50percent,
            bug_issues_closed_two_months,
        ]
