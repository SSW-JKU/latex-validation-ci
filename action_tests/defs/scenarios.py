"""
Defines various integration test scenarios and their verification steps.
"""

from gh_action_integration_test import Scenario, TestRepository


class ShootoutTestScenario(Scenario):
    """
    Simple shoot-out test scenario without verification step.
    """

    def __init__(self) -> None:
        super().__init__("shootout_test", "success")

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        print("Shoot-out tests require no verification")
