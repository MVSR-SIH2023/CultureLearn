# CultureLearn
 `README.md`: This file typically contains documentation or information about your project.
 `requirements.txt`: This file lists the dependencies (Python packages) required for your project, making it easier to install them.
  please install "GitLens — Git supercharged" extention in your vscode.
## Guidelines for commiting to the `master` branch:
* master branch is the main and important branch, therefore, it is crucial to exercise caution and consider certain factors before committing changes to it.
* Make sure that your code works perfectly without any errors
* Discuss with your teammates before commiting anything to the master branch
* Be sure to add your dependencies, required libraries to the requirements.txt
* Whenever you commit, Mention clearly what change has been done, Why it has been done, What does it actually fix or what new feature does it add in. You can also write the test cases that you're sure about.
## How to commit?
* Please be noted that, No one is allowed to commit directly to the `master` branch.
* You can push your code directly to your own branch

1. Initialize your repo (Do this only when you're uploading your code to the GitHub for the first time)
```bash
git init
```
2. Adding required files
```bash
git add <location-of-your-file-to-add>
```

3. Commiting your changes
```bash
git commit -m "Your commit message here"
# We can even write multi-line commit names
#Example:
git commit -m "Fix unable to login: fixed an issue unable to login
* There seems to be an issue with login.py, The variable was not declared." 
```

4. Pushing your changes to the GitHub:
```bash
git push HEAD:<branch-name>
```

## FAQs
* How can I create a branch?

```bash
git branch -M <branch-name>
```

* How can I delete a commit?

You can delete a commit but this is one of the dangerous tasks & it is not recommended. Make sure to ask DevOps specialist in your team.

* How can I edit my commit?

You can refer to `git rebase`, Check git documentation for that
