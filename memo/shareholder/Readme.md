Shareholder App tracks tasks, assignments, reviews and ultimately shares

Task
    creator [user who is in group shareholder]
    status [proposed(DEF), active, pending, review, completed, failed] changed by project lead
    workload [in decimal hours]
    start_date []
    closing_date []
    title
    description [jira/local task description and goals]
    feature_branch [optional name of feature branch in git]
    jira_url [optional]

Assignment
    task [FK]
    collaborator [FK user in the group shareholder]
    workload_share [1-100 % of the task total (two users with 100% would get 50% each)]
    notes [information of the collaborators role/responsibilities]

Review
    task [FK]
    reviewer [FK excluding collaborator of the task]
    rating [failed, buggy, completed, good, excellent]
    notes [explanation of rating and task]
    workload [in decimal hours]

    start_date = task.closing_date
    closing_date = task.closing_date + 1d

Board of Revenue
    A meta table listing the total of shares and monthly contributions (tasks/review)

Permissions:

Group: Shareholder:
- Task: Create, Read
- Assignment: Read
- Review: Read, Update
Group: Project Lead:
- Task: Create, Read, Update, Delete
- Assignment: Create, Read, Update, Delete
- Review: Create, Read, Update, Delete
