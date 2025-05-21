# pylint: disable=missing-module-docstring

import unittest


class TestDummy(unittest.TestCase):
    # pylint: disable=missing-class-docstring

    def setUp(self) -> None:
        super().setUp()
        self.value = 10

    def test_dummy(self) -> None:
        # pylint: disable=missing-function-docstring

        self.assertEqual(self.value, 10)


if __name__ == "__main__":
    unittest.main()
