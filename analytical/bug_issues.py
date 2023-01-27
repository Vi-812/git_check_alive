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
        self.data = data
        last_comment = None
        for bug_issue in self.data:
            if bug_issue['node']['closed']:
                self.bug_issues_closed_total_count += 1
                self.bug_issues_duration_closed_list.append(
                    fa.to_date((bug_issue['node']['closedAt'])) - fa.to_date(bug_issue['node']['createdAt'])
                )
            else:
                self.bug_issues_open_total_count += 1
                self.bug_issues_duration_open_list.append(
                    datetime.now() - fa.to_date(bug_issue['node']['createdAt'])
                )
            if not bug_issue['node']['comments']['totalCount']:
                self.bug_issues_no_comment += 1
            if bug_issue['node']['comments']['nodes']:
                last_comment = bug_issue['node']['comments']['nodes'][0]['createdAt']

    def get_bug_analytic(self):
        closed_list_len = len(self.bug_issues_duration_closed_list)
        open_list_len = len(self.bug_issues_duration_open_list)
        if closed_list_len >= 10:
            self.bug_issues_duration_closed_list.sort()
            self.duration_closed_bug_min = self.bug_issues_duration_closed_list[0]
            self.duration_closed_bug_max = self.bug_issues_duration_closed_list[-1]
            self.duration_closed_bug_95percent = self.bug_issues_duration_closed_list[round((closed_list_len - 1)
                                                                                            * 0.95)].days
            self.duration_closed_bug_50percent = median(self.bug_issues_duration_closed_list).days
        else:
            self.duration_closed_bug_min = None
            self.duration_closed_bug_max = None
            self.duration_closed_bug_95percent = None
            self.duration_closed_bug_50percent = None

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
        ]
