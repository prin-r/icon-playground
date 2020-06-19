from ..simple_price_db import SIMPLE_PRICE_DB
from tbears.libs.scoretest.score_test_case import ScoreTestCase


class TestSIMPLE_PRICE_DB(ScoreTestCase):

    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(SIMPLE_PRICE_DB, self.test_account1)

    def test_hello(self):
        self.assertEqual(self.score.hello(), "Hello")
