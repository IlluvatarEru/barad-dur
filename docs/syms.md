# Currencies and Currency Pairs

## Definitions
### Currency

A currency can be fiat (eg: `EUR`) or crypto (eg: `ETH`).
Note that a crypto-currency can have more than 3 letters, eg: `STETH`, on the other hand, fiat currencies are always 3
characteres long.

In the code, it is always written in upper case and defined in `syms.py`.

### Currency Pairs

A currency pair is formed of 2 currencies, most of the time it will be a crypto-currency and a fiat currency.
If this is indeed the case, then the fiat part will always be at the end. So: `ETHEUR` is valid but `EURETH` is not.

In the code, it is always written in upper case and defined in `syms.py`.
