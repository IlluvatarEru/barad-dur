import datetime
import os
import unittest

from core import root_folder
from core.src.date import today_date

dir_path = os.path.dirname(os.path.realpath(__file__))
root_folder.ROOT_FOLDER = dir_path + '/../../'

from core.src.column_names import MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES, \
    ASK_PRICES, MISC, TIME, OPEN, CLOSE, HIGH, LOW
from core.src.spot_syms import SUPPORTED_FIAT_CURRENCIES
from rest.src.market_data_rest_deribit_option import MarketDataRestApiDeribitOption

# INSTRUMENT = 'ETH-26MAY23-1200-C'
INSTRUMENT = 'C_ETHUSD_230630_1200'


class TestDeribitOption(unittest.TestCase):

    def test_wrong_sym_is_detected(self):
        deribit_option_api = MarketDataRestApiDeribitOption()
        wrong_sym = "X_ETHUSD_230630_1200"
        with self.assertRaises(Exception) as context:
            tob_bid = deribit_option_api.get_tob_bid(wrong_sym)
        self.assertEqual(str(context.exception).split(":")[0],
                         "Option X_ETHUSD_230630_1200 has wrong format, it should be C_LHSRHS_YYMMDD_K or P_LHSRHS_YYMMDD_K")

        wrong_sym = "C_XXXUSD_230630_1200"
        with self.assertRaises(Exception) as context:
            tob_bid = deribit_option_api.get_tob_bid(wrong_sym)
        self.assertEqual(str(context.exception).split(":")[0],
                         "Option C_XXXUSD_230630_1200 has wrong format, currency pair XXXUSD not supported")

    def test_tob_prices(self):
        deribit_option_api = MarketDataRestApiDeribitOption()
        tob_bid = deribit_option_api.get_tob_bid(INSTRUMENT)
        self.assertGreater(tob_bid, 0)

        tob_ask = deribit_option_api.get_tob_ask(INSTRUMENT)
        self.assertGreater(tob_ask, tob_bid)

        tob_mid = deribit_option_api.get_tob_mid(INSTRUMENT)
        self.assertGreater(tob_mid, tob_bid)
        self.assertLess(tob_mid, tob_ask)

        tob_spread = deribit_option_api.get_tob_spread(INSTRUMENT)
        self.assertGreater(tob_spread, 0)

    def test_orderbook(self):
        deribit_option_api = MarketDataRestApiDeribitOption()
        n_levels = 1
        ob = deribit_option_api.get_orderbook(INSTRUMENT, n_levels)
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
        deribit_option_api = MarketDataRestApiDeribitOption()
        with self.assertRaises(Exception) as context:
            fees = deribit_option_api.get_fee_schedule(INSTRUMENT)
        self.assertEqual(str(context.exception), 'This method is not supported for DERIBIT/option')

    def test_ohlc(self):
        deribit_option_api = MarketDataRestApiDeribitOption()

        # test default
        ohlc = deribit_option_api.get_ohlc(INSTRUMENT)
        max_date = ohlc[TIME].max().date()
        self.assertEqual(type(max_date), datetime.date)
        self.assertEqual(max_date, today_date())

        # with a start date
        delta = datetime.timedelta(days=-100)
        start_date = today_date() + delta
        print(f'start_date={start_date}')

        ohlc = deribit_option_api.get_ohlc(INSTRUMENT, since=start_date)
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
        deribit_option_api = MarketDataRestApiDeribitOption()
        close_price = deribit_option_api.get_close(INSTRUMENT)
        self.assertTrue(close_price >= 0)

        start_date = datetime.date(2023, 1, 1)
        close_price = deribit_option_api.get_close(INSTRUMENT, start_date)
        self.assertEqual(close_price, 0.32)
