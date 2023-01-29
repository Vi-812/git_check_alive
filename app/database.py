from analytical import github_api_client as ga
from analytical import func_api_client as fa
from app import models, db


class DataBaseHandler:
    def __init__(self):
        pass

    def get_report(self, token, repository_path, json_type='full', force=False):
        owner_name = fa.recognition(repository_path)
        self.repository_owner = owner_name['repository_owner']
        self.repository_name = owner_name['repository_name']
        self.return_json = owner_name['return_json']
        if not self.repository_owner and not self.repository_name:
            return self.return_json



        instance_api_client = ga.GithubApiClient(token)
        self.return_json = instance_api_client.get_new_report(self.repository_owner + '/' + self.repository_name, json_type)

        if self.return_json['queryInfo']['code'] == 200:
            self.save_repository()




        return self.return_json

    def save_repository(self):
        if self.return_json['queryInfo']['cost'] > 1:
            print(">>")
            self.save_statistic()

    def save_statistic(self):
        request_time = float(self.return_json['queryInfo']['time'])
        request_cost = self.return_json['queryInfo']['cost']
        statistic = models.QueryStatistics(
            name=self.return_json['repositoryInfo']['name'],
            owner_login=self.return_json['repositoryInfo']['owner'],
            issues_count=self.return_json['repositoryInfo']['issuesTotalCount'],
            bug_issues_count=self.return_json['repositoryInfo']['bugIssuesCount'],
            request_time=request_time,
            request_cost=request_cost,
            request_kf=round(request_time/request_cost, 2),
            rt=self.return_json['queryInfo']['rt']
        )
        db.session.add(statistic)
        db.session.commit()