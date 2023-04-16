import requests

def search_github_repositories(query, sort='best-match', order='desc', per_page=5):
    url = 'https://api.github.com/search/repositories'
    params = {
        'q': query,
        'sort': sort,
        'order': order,
        'per_page': per_page
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code {response.status_code}")

def find_repos(name, per_page=5):
    query = f"{name} in:name"
    res = search_github_repositories(query, per_page=per_page)
    return [{
        'name': repo['full_name'],
        'description': repo['description'],
        'stars': repo['stargazers_count'],
        'url': repo['clone_url']
    } for repo in res['items']]