# region imports
from AlgorithmImports import *
# endregion

class AdaptableSkyBlueAlpaca(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Set Start Date
        self.SetEndDate(2023,6,30)
        self.SetCash(500)  # Set Strategy Cash
        
        # Add two forex assets
        self.usd_jpy = self.AddForex("USDJPY", Resolution.Hour, Market.Oanda).Symbol
        self.eur_jpy = self.AddForex("GBPJPY", Resolution.Hour, Market.Oanda).Symbol
        self.eur_usd = self.AddForex("EURUSD", Resolution.Hour, Market.Oanda).Symbol
        self.gbp_usd = self.AddForex("GBPUSD", Resolution.Hour, Market.Oanda).Symbol
        
        
        # Lookback period for moving average and standard deviation
        self.lookback = 20

        # Create a RollingWindow to hold the recent prices, the price ratio, and the z-score
        self.price_window_usd_jpy = RollingWindow[float](self.lookback)
        self.price_window_eur_jpy = RollingWindow[float](self.lookback)
        self.price_window_eur_usd = RollingWindow[float](self.lookback)
        self.price_window_gbp_usd = RollingWindow[float](self.lookback)
        self.ratio_window = RollingWindow[float](self.lookback)
        self.zscore_window = RollingWindow[float](self.lookback)

    def OnData(self, data: Slice):
        # Add new prices to the rolling windows
        self.price_window_usd_jpy.Add(data[self.usd_jpy].Close)
        self.price_window_eur_jpy.Add(data[self.eur_jpy].Close)
        self.price_window_eur_usd.Add(data[self.eur_usd].Close)
        self.price_window_gbp_usd.Add(data[self.gbp_usd].Close)


         # Skip if we don't have enough data
        if not (self.price_window_usd_jpy.IsReady and self.price_window_eur_jpy.IsReady and self.price_window_eur_usd.IsReady and self.price_window_gbp_usd.IsReady):
            return

        # Calculate the price ratio and add it to the ratio window
        ratio = self.price_window_usd_jpy[0] / self.price_window_eur_jpy[0]
        self.ratio_window.Add(ratio)

        # Skip if we don't have enough ratio data
        if not self.ratio_window.IsReady:
            return

        # Calculate the z-score of the ratio and add it to the z-score window
        mean = np.mean([self.ratio_window[i] for i in range(self.lookback)])
        std = np.std([self.ratio_window[i] for i in range(self.lookback)])
        zscore = (ratio - mean) / std if std != 0 else 0
        self.zscore_window.Add(zscore)

        # Trading logic
        holdings_usd_jpy = self.Portfolio[self.usd_jpy].Quantity
        holdings_eur_jpy = self.Portfolio[self.eur_jpy].Quantity
        holdings_eur_usd = self.Portfolio[self.eur_usd].Quantity
        holdings_gbp_usd = self.Portfolio[self.gbp_usd].Quantity

        if zscore > -3 and holdings_usd_jpy <= 0 and holdings_eur_jpy >= 0 and holdings_eur_usd <= 0 and holdings_gbp_usd >= 0:
            # Sell EURJPY and GBPUSD, and buy USDJPY and EURUSD
            self.SetHoldings(self.eur_jpy, -0.25)
            self.SetHoldings(self.usd_jpy, 0.25)
            self.SetHoldings(self.eur_usd, 0.25)
            self.SetHoldings(self.gbp_usd, -0.25)
            # Set stop loss and take profit
            self.StopMarketOrder(self.eur_jpy, -self.Portfolio[self.eur_jpy].Quantity, 0.99 * self.Securities[self.eur_jpy].Price)
            self.StopMarketOrder(self.usd_jpy, self.Portfolio[self.usd_jpy].Quantity, 1.01 * self.Securities[self.usd_jpy].Price)
            self.StopMarketOrder(self.eur_usd, self.Portfolio[self.eur_usd].Quantity, 1.01 * self.Securities[self.eur_usd].Price)
            self.StopMarketOrder(self.gbp_usd, -self.Portfolio[self.gbp_usd].Quantity, 0.99 * self.Securities[self.gbp_usd].Price)
        elif zscore < 3 and holdings_usd_jpy >= 0 and holdings_eur_jpy <= 0 and holdings_eur_usd >= 0 and holdings_gbp_usd <= 0:
            # Sell USDJPY and EURUSD, and buy EURJPY and GBPUSD
            self.SetHoldings(self.eur_jpy, 0.25)
            self.SetHoldings(self.usd_jpy, -0.25)
            self.SetHoldings(self.eur_usd, -0.25)
            self.SetHoldings(self.gbp_usd, 0.25)
            # Set stop loss and take profit
            self.StopMarketOrder(self.eur_jpy, self.Portfolio[self.eur_jpy].Quantity, 1.01 * self.Securities[self.eur_jpy].Price)
            self.StopMarketOrder(self.usd_jpy, -self.Portfolio[self.usd_jpy].Quantity, 0.99 * self.Securities[self.usd_jpy].Price)
            self.StopMarketOrder(self.eur_usd, -self.Portfolio[self.eur_usd].Quantity, 0.99 * self.Securities[self.eur_usd].Price)
            self.StopMarketOrder(self.gbp_usd, self.Portfolio[self.gbp_usd].Quantity, 1.01 * self.Securities[self.gbp_usd].Price)
        elif abs(zscore) < 0.01:
            # Close positions
            self.Liquidate(self.eur_jpy)
            self.Liquidate(self.usd_jpy)
            self.Liquidate(self.eur_usd)
            self.Liquidate(self.gbp_usd)


