def get_info_labels_json(repository_owner, repository_name, cursor):
    json_info = {
        'query':
        """
        query GetInfo ($owner: String!, $name: String!, $cursor: String) {
            repository(name: $name, owner: $owner) {
                name
                description
                stargazerCount
                createdAt
                updatedAt
                isArchived
                labels(first: 100, after: $cursor) {
                    totalCount
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                    }
                    edges {
                        cursor
                        node {
                            name
                        }
                    }
                }
                issues {
                    totalCount
                }
            }
            rateLimit {
                cost
                remaining
                resetAt
            }
        }
        """,
        'variables': {
            "owner": repository_owner,
            "name": repository_name,
            "cursor": cursor
        }
    }
    return json_info

def get_bug_issues_json(repository_owner, repository_name, labels_bug, cursor):
    json_bug_issues = {
        'query':
        """
        query GetIssues($owner: String!, $name: String!, $labels: [String!], $cursor: String) {
            repository(name: $name, owner: $owner) {
                issues(first: 100, filterBy: {labels: $labels}, after: $cursor) {
                    totalCount
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                    }
                    edges {
                        cursor
                        node {
                            id
                            createdAt
                            closedAt
                            closed
                            updatedAt
                            comments(last: 1) {
                                totalCount
                                nodes {
                                    createdAt
                                }
                            }
                        }
                    }
                }
            }
            rateLimit {
                cost
                remaining
                resetAt
            }
        }
        """,
        'variables': {
            "owner": repository_owner,
            "name": repository_name,
            "labels": labels_bug,
            "cursor": cursor
        }
    }
    return json_bug_issues
