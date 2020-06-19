from ..my_first_score import FirstScore
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestFirstScore(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(FirstScore, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
