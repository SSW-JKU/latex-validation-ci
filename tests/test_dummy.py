import unittest


class TestDummy(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.value = 10

    def test_dummy(self) -> None:
        assert self.value == 10


if __name__ == "__main__":
    unittest.main()
