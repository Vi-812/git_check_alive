from statistics import median
from datetime import datetime
import analytical.func_api_client as fa


class BugIssuesAnalytic():
    def __init__(self):
        self.bug_issues = {
            'id': [],
            'title': [],
            'created_at': [],
            'updated_at': [],
            'closed_at': [],
            'closed_bool': [],
            'comments_count': [],
            'comments_last': [],
        }

    def push_bug_issues(self, data):
        self.data = data
        for bug_issue in self.data:
            self.bug_issues['id'].append(bug_issue['node']['id'])
            self.bug_issues['title'].append(bug_issue['node']['title'])
            self.bug_issues['created_at'].append(bug_issue['node']['createdAt'])
            self.bug_issues['updated_at'].append(bug_issue['node']['updatedAt'])
            self.bug_issues['closed_at'].append(bug_issue['node']['closedAt'])
            self.bug_issues['closed_bool'].append(bug_issue['node']['closed'])
            self.bug_issues['comments_count'].append(bug_issue['node']['comments']['totalCount'])
            if bug_issue['node']['comments']['nodes']:
                self.bug_issues['comments_last'].append(bug_issue['node']['comments']['nodes'][0]['createdAt'])
            else:
                self.bug_issues['comments_last'].append(None)

    def get_bug_analytic(self):
        self.bug_issues_closed_total_count = 0
        self.bug_issues_open_total_count = 0
        self.bug_issues_duration_all_list = []
        self.bug_issues_duration_closed_list = []
        self.bug_issues_duration_open_list = []
        list_len = len(self.bug_issues['id'])
        validation_list = all(map(lambda lst: len(lst) == list_len, [
            self.bug_issues['title'],
            self.bug_issues['created_at'],
            self.bug_issues['updated_at'],
            self.bug_issues['closed_at'],
            self.bug_issues['closed_bool'],
            self.bug_issues['comments_count'],
            self.bug_issues['comments_last'],
        ]))
        if not validation_list:
            print('Ошибка! Несоответствие при валидации длинны массивов bug_issues!')
        for i in range(list_len):
            self.bug_issues['created_at'][i] = fa.to_date(self.bug_issues['created_at'][i])
            if bool(self.bug_issues['closed_at'][i]) and self.bug_issues['closed_bool'][i]:
                self.bug_issues_closed_total_count += 1
                self.bug_issues['closed_at'][i] = fa.to_date(self.bug_issues['closed_at'][i])
                duration = self.bug_issues['closed_at'][i] - self.bug_issues['created_at'][i]
                self.bug_issues_duration_all_list.append(duration)
                self.bug_issues_duration_closed_list.append(duration)
            elif not bool(self.bug_issues['closed_at'][i]) and not self.bug_issues['closed_bool'][i]:
                self.bug_issues_open_total_count += 1
                self.bug_issues_duration_all_list.append(None)  # ??? --------------------------------
                self.bug_issues_duration_open_list.append(datetime.now() - self.bug_issues['created_at'][i])
            else:
                print(f'Ошибка! Несоответствие информации о закрытии issues с id = {self.bug_issues["id"][i]}, '
                      f'closed = {self.bug_issues["closed_bool"][i]}, '
                      f'closed_at = {self.bug_issues["closed_at"][i]}')
            self.bug_issues['updated_at'][i] = fa.to_date(self.bug_issues['updated_at'][i])
            if self.bug_issues['comments_last'][i]:
                self.bug_issues['comments_last'][i] = fa.to_date(self.bug_issues['comments_last'][i])

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
            self.duration_closed_bug_min,
            self.duration_closed_bug_max,
            self.duration_closed_bug_95percent,
            self.duration_closed_bug_50percent,
            self.duration_open_bug_min,
            self.duration_open_bug_max,
            self.duration_open_bug_50percent,
        ]
