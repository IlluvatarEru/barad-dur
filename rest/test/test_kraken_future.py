import datetime
import os
import unittest

from core import root_folder
from core.src.column_names import MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES, \
    ASK_PRICES, MISC, HIGH, LOW, OPEN, CLOSE, TIME
from core.src.date import today_date, MINUTES_PER_DAY
from core.src.syms import ETHUSD, SUPPORTED_FIAT_CURRENCIES

dir_path = os.path.dirname(os.path.realpath(__file__))
root_folder.ROOT_FOLDER = dir_path + '/../../'

from rest.src.market_data_rest_kraken_spot import MarketDataRestApiKrakenSpot
from rest.src.market_data_rest_kraken_future import MarketDataRestApiKrakenFuture


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
        kraken_future_api = MarketDataRestApiKrakenFuture()
        n_levels = 3
        sym = "PF_USDCUSD"
        ob = kraken_future_api.get_orderbook(sym, n_levels)
        print(ob)
        self.assertEqual(ob.columns.tolist(),
                         [MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES,
                          ASK_PRICES,
                          MISC])
        self.assertEqual(len(ob), 1)
        self.assertEqual(len(ob[BID_SIZES].values[0]), n_levels)
        self.assertEqual(len(ob[BID_PRICES].values[0]), n_levels)
        self.assertEqual(len(ob[ASK_SIZES].values[0]), n_levels)
        self.assertEqual(len(ob[ASK_PRICES].values[0]), n_levels)

        self.assertTrue(ob[BID_SIZES].values[0][0] >= 0)
        self.assertTrue(ob[BID_PRICES].values[0][0] >= 0)
        self.assertTrue(ob[ASK_SIZES].values[0][0] >= 0)
        self.assertTrue(ob[ASK_PRICES].values[0][0] >= 0)

    def test_fee_schedule(self):
        kraken_spot_api = MarketDataRestApiKrakenSpot()
        fees = kraken_spot_api.get_fee_schedule(ETHUSD)
        self.assertTrue(len(fees['fees_taker']) > 0)
        self.assertTrue(len(fees['fees_maker']) > 0)
        self.assertTrue(fees['fees_taker'][0][1] >= 0)
        self.assertTrue(fees['fees_taker'][0][1] >= 0)
        self.assertTrue(fees['fee_volume_currency'] in SUPPORTED_FIAT_CURRENCIES)

    def test_ohlc(self):
        kraken_spot_api = MarketDataRestApiKrakenSpot()
        ohlc = kraken_spot_api.get_ohlc(ETHUSD)
        max_date = ohlc[TIME].max().date()
        self.assertEqual(type(max_date), datetime.date)
        self.assertEqual(max_date, today_date())

        # test with a start date
        # Actually the Kraken endpoint is broken and it will just return data for the last 720 ticks,
        # the "since" argument has no impact
        delta = datetime.timedelta(days=-719)
        start_date = today_date() + delta
        # 1440 min every day
        interval = MINUTES_PER_DAY
        ohlc = kraken_spot_api.get_ohlc(ETHUSD, interval=interval)

        # check dates are as expected
        max_date = ohlc[TIME].max().date()
        min_date = ohlc[TIME].min().date()
        self.assertEqual(type(max_date), datetime.date)
        self.assertEqual(max_date, today_date())
        self.assertEqual(min_date, start_date)

        # check prices are >=0
        self.assertTrue(ohlc.iloc[0][OPEN] >= 0)
        self.assertTrue(ohlc.iloc[0][CLOSE] >= 0)
        self.assertTrue(ohlc.iloc[0][HIGH] >= 0)
        self.assertTrue(ohlc.iloc[0][LOW] >= 0)

    def test_close(self):
        kraken_spot_api = MarketDataRestApiKrakenFuture()
        close_price = kraken_spot_api.get_close(ETHUSD)
        self.assertTrue(close_price >= 0)

        start_date = datetime.date(2023, 1, 1)
        close_price = kraken_spot_api.get_close(ETHUSD, start_date)
        self.assertEqual(close_price, 1199.76)
