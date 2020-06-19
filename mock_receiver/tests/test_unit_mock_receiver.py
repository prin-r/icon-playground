from ..mock_receiver import MOCK_RECEIVER
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestMOCK_RECEIVER(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(MOCK_RECEIVER, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
