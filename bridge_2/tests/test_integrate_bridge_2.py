import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import (
    DeployTransactionBuilder,
    CallTransactionBuilder,
)
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestTest(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        self._score_address = self._deploy_score()['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder().from_(self._test1.get_address()).to(to).step_limit(100_000_000_000).nid(
            3).nonce(100).content_type("application/zip").content(gen_deploy_data_content(self.SCORE_PROJECT)).build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(
            signed_transaction, self.icon_service)

        self.assertEqual(True, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        # update SCORE
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_call_hello(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()).to(
            self._score_address).method("hello").build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        self.assertEqual("Hello", response)

    def test_call_get_test(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()).to(
            self._score_address).method("get_test").build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        self.assertEqual(
            "aa58d2b0be1dbadf21619645c9245062a283c19a6701bfe07d07cc2441687c85", response)

    # def test_call_get_test_2(self):
    #     params = {}
    #     params["data"] = "32fa694879095840619f5e49380612bd296ff7e950eafb66ff654d99ca70869e4baef831b309c193cc94dcf519657d832563b099a6f62c6fa8b7a043ba4f3b3b5e1a8142137bdad33c3875546e42201c050fbccdcf33ffc15ec5b60d09803a25004209a161040ab1778e2f2c00ee482f205b28efba439fcb04ea283f619478d96e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d0cf1e6ece60e49d19bb57c1a432e805f39bb4f65c366741e4f03fa54fbd90714"
    #     params["app_hash"] = "1CCD765C80D0DC1705BB7B6BE616DAD3CF2E6439BB9A9B776D5BD183F89CA141"
    #     params["block_height"] = 381837

    #     transaction = CallTransactionBuilder().from_(self._test1.get_address()).to(
    #         self._score_address).step_limit(100_000_000_000).nid(
    #         3).nonce(100).method("set_test").params(params).build()

    #     signed_transaction = SignedTransaction(transaction, self._test1)

    #     tx_result = self.process_transaction(
    #         signed_transaction, self.icon_service)

    #     self.assertEqual(True, tx_result['status'])

    #     # Generates a call instance using the CallBuilder
    #     call = CallBuilder().from_(self._test1.get_address()).to(
    #         self._score_address).method("get_test").build()

    #     # Sends the call request
    #     response = self.process_call(call, self.icon_service)

    #     self.assertEqual(
    #         "a35617a81409ce46f1f820450b8ad4b217d99ae38aaa719b33c4fc52dca99b22", response)
