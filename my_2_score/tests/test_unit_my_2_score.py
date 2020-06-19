from ..my_2_score import momo
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class Testmomo(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(momo, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
