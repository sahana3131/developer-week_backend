'''
============= Helpers ============= 
'''

def get_file_content(gh, repo, get_file):
    return gh.get_repo(f"{gh.get_user().login}/{repo}").get_contents(get_file).decoded_content.decode()

def get_files(gh, repo):
    return [{"file":file.name} for file in gh.get_repo(f"{gh.get_user().login}/{repo}").get_contents("/")]

def get_repos(gh):
    print('get_repos')
    return {
         'user' : gh.get_user().login,
        'repo': [{"repo": f"{repo.name}"} for repo in gh.get_user().get_repos() ]

    }

def get_visitors(repo):
    timestamp = []
    count = []
    for view in repo.get_views_traffic()["views"]:
        timestamp.append(view.timestamp)
        count.append(view.count)
    return [{"timestamp": timestamp, "count": count}]

def get_clones(repo):
    timestamp = []
    count = []
    for view in repo.get_clones_traffic()["clones"]:
        timestamp.append(view.timestamp)
        count.append(view.count)
    return [{"timestamp": timestamp, "count": count}]

def get_analytics(repo):
    data = {
        "stars": repo.watchers_count,
        "forks": repo.forks_count,
        "contributors": repo.get_contributors().totalCount,
        "issues": repo.open_issues_count,
        "pull_requests": repo.get_pulls().totalCount,
        "commits": repo.get_commits().totalCount,
        "releases": repo.get_releases().totalCount,
        "branches": repo.get_branches().totalCount,
        "total_clones": repo.get_clones_traffic()["count"]
    }

    return data

def get_referral_sources(repo):
    return [{"source": source.referrer} for source in repo.get_top_referrers()]

def get_languages(repo):
    return [{"language": language} for language in repo.get_languages()]

def get_repo_content(gh, repo):
    '''
    data = {
        files : [
            {
                file: "app.py"
            },
            {
                file: "main.py"
            }
        ],
        analytics : {
            stars : 100,
            forks : 100,
            contributors : 100,
            issues : 100,
            pull_requests : 100,
            commits : 100,
            releases : 100,
            branches : 100, 
            page_views : 100,
        },
        referral_sources : [
            {
                source: "google",
            },
            {
                source: "github",
            }
        ],
        visitors : [
            {
                timestamp : "2021-01-01 00:00:00",
                counts : 100,
                }
        ],
        clones : [
            {
                timestamp : "2021-01-01 00:00:00",
                clones : 100,
            }
        ],
        languages : [
            {
                language: "python", 
            }, 
        ],
        repo : "repo_name"
    }
    '''

    print('get_repo_content' , repo , gh)

    r = gh.get_repo(f"{gh.get_user().login}/{repo}")
    data = {
        "files": get_files(gh, repo),
        "analytics": get_analytics(r),
        "referral_sources": get_referral_sources(r),
        "visitors": get_visitors(r),
        "clones": get_clones(r),
        "languages": get_languages(r),
        "repo": repo
    }

    return data