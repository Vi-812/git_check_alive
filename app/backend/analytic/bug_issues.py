from statistics import median
from datetime import datetime
import app.backend.analytic.functions as fn


class BugIssuesAnalytic:
    """
    Анализ полученных bug_issues.
    :param data: данные о bug_issues (json/GitHub)
    :return: аналитику по bug_issues
    """
    def __init__(self):
        self.bug_issues_closed_total_count = 0
        self.bug_issues_open_total_count = 0
        self.bug_issues_no_comment = 0
        self.bug_issues_duration_closed_list = []
        self.bug_issues_duration_open_list = []

    async def push_bug_issues(self, github_data):
        now_time = datetime.utcnow()
        for bug_issue in github_data:  # Перебираем полученные bug_issues, собираем промежуточную статистику
            created_at = await fn.to_date(bug_issue['node']['createdAt'])
            comment_count = bug_issue['node']['comments']['totalCount']
            if bug_issue['node']['comments']['nodes']:  # Когда был последний комментарий (пока не используется)
                last_comment = bug_issue['node']['comments']['nodes'][0]['createdAt']
            else:
                last_comment = None

            if bug_issue['node']['closed']:  # Если bug_issue закрыта, собираем в одну статистику
                closed_at = await fn.to_date(bug_issue['node']['closedAt'])
                self.bug_issues_closed_total_count += 1
                self.bug_issues_duration_closed_list.append(closed_at - created_at)
            else:  # Если открыто в другую
                self.bug_issues_open_total_count += 1
                self.bug_issues_duration_open_list.append(now_time - created_at)
            if not comment_count:  # Считаем сколько bug_issues вообще без комментариев
                self.bug_issues_no_comment += 1

    async def get_bug_analytic(self, resp_json):
        closed_list_len = len(self.bug_issues_duration_closed_list)
        open_list_len = len(self.bug_issues_duration_open_list)  # Пока не используется
        bug_issues_closed2m = None
        if closed_list_len >= 10:  # Если bug_issues меньше 10, статистику не считаем
            bug_issues_closed2m = 0
            self.bug_issues_duration_closed_list.sort()

            # За какое время было закрыто 95 процентов bug_issues (в днях)
            resp_json.data.closed_bug_95perc = self.bug_issues_duration_closed_list[
                round((closed_list_len - 1) * 0.95)
            ].days

            # За какое время было закрыто 50 процентов bug_issues (в днях)
            resp_json.data.closed_bug_50perc = median(self.bug_issues_duration_closed_list).days

            # Сколько (штук) bug_issues было закрыто меньше чем за 2 месяца (не 2 последних)
            for i in range(closed_list_len):
                if self.bug_issues_duration_closed_list[i].days < 60:
                    bug_issues_closed2m += 1
                else:
                    break

        resp_json.data.bug_issues_closed_count = self.bug_issues_closed_total_count
        resp_json.data.bug_issues_open_count = self.bug_issues_open_total_count

        # Сколько bug_issues без комментариев, в процентном соотношении
        if resp_json.data.bug_issues_count:
            resp_json.data.bug_issues_no_comment = round(
                self.bug_issues_no_comment / resp_json.data.bug_issues_count * 100, 2
            )

        # Сколько bug_issues было закрыто меньше чем за 2 месяца (в процентном соотношении)
        if resp_json.data.bug_issues_closed_count and bug_issues_closed2m:
            resp_json.data.bug_issues_closed2m = round(
                bug_issues_closed2m / resp_json.data.bug_issues_closed_count * 100, 2
            )
        return resp_json
