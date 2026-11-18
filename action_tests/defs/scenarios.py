"""
Defines various integration test scenarios and their verification steps.
"""

from gh_action_integration_test.git.repository import TestRepository
from gh_action_integration_test.scenario import Scenario


class ShootoutTestScenario(Scenario):
    """
    Simple shoot-out test scenario without verification step.
    """

    def __init__(self) -> None:
        super().__init__("shootout_test", "success")

    def _prepare_repository(self, repo: TestRepository) -> None:
        pass

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        print("Shoot-out tests require no verification")
