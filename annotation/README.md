Tool: Github Issue Data Annotation tool for building bug taxonomy

We have 4 .json files containing Github issues from 4 applications:
- bookstack
- indico
- invoiceninja
- prestashop

Each of them will have the following schema as an example:
```
    {
        "url": "https://api.github.com/repos/BookStackApp/BookStack/issues/5779",
        "repository_url": "https://api.github.com/repos/BookStackApp/BookStack",
        "labels_url": "https://api.github.com/repos/BookStackApp/BookStack/issues/5779/labels{/name}",
        "comments_url": "https://api.github.com/repos/BookStackApp/BookStack/issues/5779/comments",
        "events_url": "https://api.github.com/repos/BookStackApp/BookStack/issues/5779/events",
        "html_url": "https://github.com/BookStackApp/BookStack/issues/5779",
        "id": 3363524573,
        "node_id": "I_kwDOAnqaWc7Ie0_d",
        "number": 5779,
        "title": "Notification Preferences missing if user does not have the Admin role",
        "user": {
            "login": "Kofl",
            "id": 6079097,
            "node_id": "MDQ6VXNlcjYwNzkwOTc=",
            "avatar_url": "https://avatars.githubusercontent.com/u/6079097?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/Kofl",
            "html_url": "https://github.com/Kofl",
            "followers_url": "https://api.github.com/users/Kofl/followers",
            "following_url": "https://api.github.com/users/Kofl/following{/other_user}",
            "gists_url": "https://api.github.com/users/Kofl/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/Kofl/starred{/owner},{/repo}",
            "subscriptions_url": "https://api.github.com/users/Kofl/subscriptions",
            "organizations_url": "https://api.github.com/users/Kofl/orgs",
            "repos_url": "https://api.github.com/users/Kofl/repos",
            "events_url": "https://api.github.com/users/Kofl/events{/privacy}",
            "received_events_url": "https://api.github.com/users/Kofl/received_events",
            "type": "User",
            "user_view_type": "public",
            "site_admin": false
        },
        "labels": [
            {
                "id": 254047490,
                "node_id": "MDU6TGFiZWwyNTQwNDc0OTA=",
                "url": "https://api.github.com/repos/BookStackApp/BookStack/labels/:bug:%20Bug",
                "name": ":bug: Bug",
                "color": "db6257",
                "default": false,
                "description": ""
            }
        ],
        "state": "closed",
        "locked": false,
        "assignee": null,
        "assignees": [],
        "milestone": null,
        "comments": 3,
        "created_at": "2025-08-28T14:21:18Z",
        "updated_at": "2025-08-28T17:12:56Z",
        "closed_at": "2025-08-28T17:00:11Z",
        "author_association": "NONE",
        "type": null,
        "active_lock_reason": null,
        "sub_issues_summary": {
            "total": 0,
            "completed": 0,
            "percent_completed": 0
        },
        "issue_dependencies_summary": {
            "blocked_by": 0,
            "total_blocked_by": 0,
            "blocking": 0,
            "total_blocking": 0
        },
        "body": "### Describe the Bug\n\nHi,\n\nrunning latest BookStack v25.07.1\n\nIts reproduceable so far, when a user does not have the admin role assigned, the options for \"Notification Preferences\" under \"My account\" are missing.\n\nUser has only Editor permissions:\n\n<img width=\"314\" height=\"268\" alt=\"Image\" src=\"https://github.com/user-attachments/assets/54569bc2-d79c-4857-9321-90c868fff25d\" />\n\nSame User with Admin permissions:\n\n<img width=\"297\" height=\"356\" alt=\"Image\" src=\"https://github.com/user-attachments/assets/c4b3dd48-f41e-4ee4-88b1-960e57bcf8a8\" />\n\n\n\n\n### Steps to Reproduce\n\nAssign user admin permissions => Notification Preferences visible\nAssign user only editor permissions => Notification Preferences not visible\n\n### Expected Behaviour\n\nindependent of the user permission, Notification Preferences should always be visible.\n\n### Screenshots or Additional Context\n\n_No response_\n\n### Browser Details\n\n_No response_\n\n### Exact BookStack Version\n\n25.07.1",
        "closed_by": {
            "login": "Kofl",
            "id": 6079097,
            "node_id": "MDQ6VXNlcjYwNzkwOTc=",
            "avatar_url": "https://avatars.githubusercontent.com/u/6079097?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/Kofl",
            "html_url": "https://github.com/Kofl",
            "followers_url": "https://api.github.com/users/Kofl/followers",
            "following_url": "https://api.github.com/users/Kofl/following{/other_user}",
            "gists_url": "https://api.github.com/users/Kofl/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/Kofl/starred{/owner},{/repo}",
            "subscriptions_url": "https://api.github.com/users/Kofl/subscriptions",
            "organizations_url": "https://api.github.com/users/Kofl/orgs",
            "repos_url": "https://api.github.com/users/Kofl/repos",
            "events_url": "https://api.github.com/users/Kofl/events{/privacy}",
            "received_events_url": "https://api.github.com/users/Kofl/received_events",
            "type": "User",
            "user_view_type": "public",
            "site_admin": false
        },
        "reactions": {
            "url": "https://api.github.com/repos/BookStackApp/BookStack/issues/5779/reactions",
            "total_count": 0,
            "+1": 0,
            "-1": 0,
            "laugh": 0,
            "hooray": 0,
            "confused": 0,
            "heart": 0,
            "rocket": 0,
            "eyes": 0
        },
        "timeline_url": "https://api.github.com/repos/BookStackApp/BookStack/issues/5779/timeline",
        "performed_via_github_app": null,
        "state_reason": "completed"
    },
```


Main requirements of this tool:
- Screen 1: listing of annotated and unannotated issues:
  - User see list of remaining unannotated issues by applications, choosing each will filter out accordingly and show the current count.
  - Should be fast and .json based.****
  - User can quickly search for issue based on name or number (simple search algorithm, only needs to check 2 fields).
  - ABLE to show unannotated and annotated records.
- Screen 2: annotation screen:
  - On the left should show main information of the issue, link to the original issue, render the body of the issue similar to what's shown in a Github issue page.
  - On the right the annotator can choose labels to assign to this issue. 1 issue can have multiple labels.
  - Annotator can create new label to assign on the fly.
  - When saved, it will save to the resulting .json file and make sure there is no data contamination.
- Feature 3: user workspace
  - Data is splitted into splits by each user, .i.e. ./data/splits/minh then it's for user `minh`.
  - We can see each user's annotation progress (how many annotated and how many not annotated, ...) and do annotation for the records in that user as well.
  - We will manage the annotations so that it will be per-application and per-user to avoid conflict. The results of annotation should be saved in a separate files.
  - Different users will share different labels files as well.

Technical requirements:
- The data should be .json files based and have realtime update to the file.
- Minimal, functioning website don't introduce redundant code or functionalities. Visually simple is enough.