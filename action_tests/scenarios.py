"""
Defines various integration test scenarios and their verification steps.
"""

from action_tests.scenario import Scenario, ScenarioManager

from .test_repository import TestRepository

SUCCESS_OUTCOME = "success"
FAILURE_OUTCOME = "failure"


class ShootoutTestScenario(Scenario):
    """
    Simple shoot-out test scenario without verification step.
    """

    def __init__(self) -> None:
        super().__init__("shootout_test", SUCCESS_OUTCOME)

    def verify(self, repo: TestRepository) -> None:
        print(f"Verifying scenario: {self.name}")
        print("Shoot-out tests require no verification")


SCENARIOS = ScenarioManager(ShootoutTestScenario())
