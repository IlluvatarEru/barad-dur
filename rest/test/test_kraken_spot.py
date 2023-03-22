import os
import unittest

from core import root_folder
from core.src.column_names import MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES, \
    ASK_PRICES, MISC
from core.src.syms import ETHUSD, SUPPORTED_FIAT_CURRENCIES

dir_path = os.path.dirname(os.path.realpath(__file__))
root_folder.ROOT_FOLDER = dir_path + '/../../'

from rest.src.market_data_rest_kraken import MarketDataRestApiKrakenSpot


class TestKrakenSpot(unittest.TestCase):

    def test_tob_prices(self):
        kraken_spot_api = MarketDataRestApiKrakenSpot()
        tob_bid = kraken_spot_api.get_tob_bid(ETHUSD)
        self.assertGreater(tob_bid, 0)

        tob_ask = kraken_spot_api.get_tob_ask(ETHUSD)
        self.assertGreater(tob_ask, tob_bid)

        tob_mid = kraken_spot_api.get_tob_mid(ETHUSD)
        self.assertGreater(tob_mid, tob_bid)
        self.assertLess(tob_mid, tob_ask)

        tob_spread = kraken_spot_api.get_tob_spread(ETHUSD)
        self.assertGreater(tob_spread, 0)

    def test_orderbook(self):
        kraken_spot_api = MarketDataRestApiKrakenSpot()
        n_levels = 3
        ob = kraken_spot_api.get_orderbook(ETHUSD, n_levels)
        self.assertEqual(ob.columns.tolist(),
                         [MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES, ASK_PRICES,
                          MISC])
        self.assertEqual(len(ob), 1)
        self.assertEqual(len(ob[BID_SIZES].values[0]), n_levels)
        self.assertEqual(len(ob[BID_PRICES].values[0]), n_levels)
        self.assertEqual(len(ob[ASK_SIZES].values[0]), n_levels)
        self.assertEqual(len(ob[ASK_PRICES].values[0]), n_levels)

    def test_fee_schedule(self):
        kraken_spot_api = MarketDataRestApiKrakenSpot()
        fees = kraken_spot_api.get_fee_schedule(ETHUSD)
        self.assertTrue(len(fees['fees_taker']) > 0)
        self.assertTrue(len(fees['fees_maker']) > 0)
        self.assertTrue(fees['fees_taker'][0][1] >= 0)
        self.assertTrue(fees['fees_taker'][0][1] >= 0)
        self.assertTrue(fees['fee_volume_currency'] in SUPPORTED_FIAT_CURRENCIES)
