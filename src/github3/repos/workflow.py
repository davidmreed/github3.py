"""This module contains Workflows objects.

These objects represent runs of workflows in GitHub Actions
for a repository.
"""

from collections import namedtuple
from typing import NamedTuple
from .. import models

class Workflow(models.GitHubCore):
    ...

    def disable(self):
        ...

    def enable(self):
        ...

    def dispatch(self):
        ...

    def runs(self):
        ...

class Run(models.GitHubCore):

    def _repr(self):
        return f"<{self.class_name} [{self}]>"

    def __str__(self):
        return self.id

    def workflow(self):
        return self.repository.workflow(self.workflow_id)

    def _update_attributes(self, run):
        from github3.repos.repo import ShortRepository
        from github3.users import ShortUser

        self.id = run["id"]
        self.name = run["name"]
        self.node_id = run["node_id"]
        self.check_suite_id = run["check_suite_id"]
        self.check_suite_node_id = run["check_suite_node_id"]
        self.head_branch = run["head_branch"]
        self.head_sha = run["head_sha"]
        self.path = run["path"]
        self.run_number = run["run_number"]
        self.event = run["event"]
        self.display_title = run["display_title"]
        self.status = run["status"]
        self.conclusion = run["conclusion"]
        self.workflow_id = run["workflow_id"]
        self.repository = ShortRepository(run["repository"], self)
        self.url = run["url"]
        self.html_url = run["html_url"]
        self.created_at = self._strptime(run["created_at"])
        self.updated_at = self._strptime(run["updated_at"])
        self.run_attempt = run["run_attempt"]
        self.actor = ShortUser(run["actor"], self)
        self.run_started_at = self._strptime((run["run_started_at"]))
        self.triggering_actor = ShortUser(run["triggering_actor"], self)
        self.repository = ShortRepository(run["repository"], self) # to verify
        self.head_repository = ShortRepository(run["head_repository"], self) # to verify
#   "pull_requests": [],
#   "referenced_workflows": [
#     {
#       "path": "octocat/Hello-World/.github/workflows/deploy.yml@main",
#       "sha": "86e8bc9ecf7d38b1ed2d2cfb8eb87ba9b35b01db",
#       "ref": "refs/heads/main"
#     },
#     {
#       "path": "octo-org/octo-repo/.github/workflows/report.yml@v2",
#       "sha": "79e9790903e1c3373b1a3e3a941d57405478a232",
#       "ref": "refs/tags/v2"
#     },
#     {
#       "path": "octo-org/octo-repo/.github/workflows/secure.yml@1595d4b6de6a9e9751fb270a41019ce507d4099e",
#       "sha": "1595d4b6de6a9e9751fb270a41019ce507d4099e"
#     }
#   ],
#   "jobs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/jobs",
#   "logs_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/logs",
#   "check_suite_url": "https://api.github.com/repos/octo-org/octo-repo/check-suites/414944374",
#   "artifacts_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/artifacts",
#   "cancel_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/cancel",
#   "rerun_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/rerun",
#   "previous_attempt_url": "https://api.github.com/repos/octo-org/octo-repo/actions/runs/30433642/attempts/1",
#   "workflow_url": "https://api.github.com/repos/octo-org/octo-repo/actions/workflows/159038",
#   "head_commit": {
#     "id": "acb5820ced9479c074f688cc328bf03f341a511d",
#     "tree_id": "d23f6eedb1e1b9610bbc754ddb5197bfe7271223",
#     "message": "Create linter.yaml",
#     "timestamp": "2020-01-22T19:33:05Z",
#     "author": {
#       "name": "Octo Cat",
#       "email": "octocat@github.com"
#     },
#     "committer": {
#       "name": "GitHub",
#       "email": "noreply@github.com"
#     }
#   },
# }

    @decorators.authentication_required
    def re_run(self):
        url = build_url(["repos", "owner", "repo", "actions", "runs", self.id, "rerun"])
        self._post(
            url, headers=headers, data=data
        )
        # 201 created is success

    def re_run_failed(self):
        url = build_url(["repos", "owner", "repo", "actions", "runs", self.id, "rerun-failed-jobs"])
        self._post(
            url, headers=headers, data=data
        )
        # 201 created is success
    
    def download_logs(self):
        url = build_url(["repos", "owner", "repo", "actions", "runs", self.id, "logs"])
        self._get(
            url, headers=headers, data=data
        )
        # We get back a `Location:` redirect header

    def delete(self):
        ...
    
    def cancel(self):
        ...

    def attempts(self):
        ...

    def jobs(
        self,
        count=-1,
        all: bool = False
    ):
        """Iterate over the jobs for this workflow run.

        :param bool all:
            (optional), return jobs from all workflow run attempts
        :returns:
            generator of workflow run jobs
        :rtype:
            :class:`~github3.repos.workflow.Job`
        """

        url = self.repo._build_url("actions", "runs", self.id, "jobs", base_url=self._api)

        return self._iter(
            int(count),
            url,
            Job,
            params={"filter": "all" if all else "latest"}
            list_key="jobs",
        )


class Step(NamedTuple):
    name: str
    status: str
    conclusion: str
    number: int
    started_at: datetime
    completed_at: datetime

class Job(models.GitHubCore):
    def workflow_run(self):
        return self.repository.workflow_run(self.run_id)


    def _update_attributes(self, job):
        from github3.repos.repo import ShortRepository
        from github3.users import ShortUser

        attributes = [
                "id",
                "node_id",
                "run_id",
                "run_url",
                "head_sha",
                "workflow_name",
                "head_branch",
                "name",
                "url",
                "html_url",
                "status",
                "conclusion",
                ("started_at", self._strptime),
                ("completed_at", self._strptime),
                "check_run_url",
                "labels",
                "runner_id",
                "runner_name",
                "runner_group_id",
                "runner_group_name",
                ("created_at", self._strptime),
                ("steps", lambda s: [Step(**k) for k in s])
        ]

        for attribute in attributes:
            if type(attribute) is tuple:
                json_key, attribute_name, converter = attribute
            else:
                json_key = attribute_name = attribute
                converter = lambda x: x
            setattr(self, attribute_name, converter(job[json_key]))


class Usage(models.GitHubCore):
    
    def _update_attributes(self, json):
        # TODO: resilience
        self.ubuntu = json["billable"]["UBUNTU"]["total_ms"]
        self.macos = json["billable"]["UBUNTU"]["total_ms"]
        self.windows = json["billable"]["WINDOWS"]["total_ms"]

   