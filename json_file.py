def get_info_json(repository_owner, repository_name, cursor):
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