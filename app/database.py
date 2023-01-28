from analytical import github_api_client
from analytical import func_api_client as fa


class DataBaseHandler:
    def __init__(self):
        pass

    def get_report(self, token, repository_path):

        owner_name = fa.recognition(repository_path)
        self.repository_owner = owner_name['repository_owner']
        self.repository_name = owner_name['repository_name']
        self.return_json = owner_name['return_json']
        if not self.repository_owner and not self.repository_name:
            return self.return_json





        instance_api_client = github_api_client.GithubApiClient(token)
        return_json = instance_api_client.get_new_report(self.repository_owner + '/' + self.repository_name)
        return return_json