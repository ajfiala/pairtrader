# region imports
from AlgorithmImports import *
# endregion

###########################
# OPTIMIZED PARAMETERS:
# zscore_positive: 3.1
# zscore_negative: -2.1
###########################

class ParameterizedAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Set Start Date
        self.SetEndDate(2023,7,21)
        self.SetCash(500)  # Set Strategy Cash
        
        self.pairs = ["GBPJPY", "USDJPY"]
        self.ratio = self.pairs[0][:3] + self.pairs[1][:3]

        # Add forex assets and their corresponding RSI indicators
        self.usd_jpy = self.AddForex(self.pairs[0], Resolution.Hour, Market.Oanda).Symbol
        self.usdjpyrsi = self.RSI(self.usd_jpy, 14)

        self.gbp_jpy = self.AddForex(self.pairs[1], Resolution.Hour, Market.Oanda).Symbol
        self.gbpjpyrsi = self.RSI(self.gbp_jpy, 14)

        # Lookback period for moving average and standard deviation
        # self.lookback = float(self.GetParameter("lookback"))
        self.threshold = -0.01
        self.lookback = 20
        self.returns_lookback = 40
        self.zscore_positive = float(self.GetParameter("zscore_positive"))
        self.zscore_negative = float(self.GetParameter("zscore_negative"))
        self.returns = RollingWindow[float](self.returns_lookback)  # define a RollingWindow to store returns
        self.prev_portfolio_value = self.Portfolio.TotalPortfolioValue
        # Create a dictionary to hold the RollingWindows for each symbol
        self.price_windows = {
            self.pairs[0]: RollingWindow[float](self.lookback),
            self.pairs[1]: RollingWindow[float](self.lookback),
           
        }
        self.max_portfolio_value = 500
        self.ratio_windows = {
            self.ratio: RollingWindow[float](self.lookback)
           
        }

        self.zscore_windows = {
            self.ratio: RollingWindow[float](self.lookback)
        }

    def OnData(self, data: Slice):
        # Check if the drawdown limit has been reached
        
        # drawdown = (self.max_portfolio_value - self.Portfolio.TotalPortfolioValue) / self.max_portfolio_value
        # if drawdown > 0.09:
        #     self.Liquidate()
        #     return
        self.max_portfolio_value = max(self.max_portfolio_value, self.Portfolio.TotalPortfolioValue)

       
        # Then in the OnData method, calculate the daily return like this:
        if self.prev_portfolio_value != 0:  # Avoid division by zero
            daily_return = (self.Portfolio.TotalPortfolioValue - self.prev_portfolio_value) / self.prev_portfolio_value
            self.returns.Add(daily_return)

         # Don't forget to update the previous portfolio value for the next step
        self.prev_portfolio_value = self.Portfolio.TotalPortfolioValue


        # Calculate the daily return and add it to the RollingWindow
        daily_return = (self.Portfolio.TotalPortfolioValue - self.prev_portfolio_value) / self.prev_portfolio_value
        self.Log(daily_return)
        self.returns.Add(daily_return)
        
        # Calculate the moving average of returns
        moving_average_return = np.mean([self.returns[i] for i in range(self.lookback)])
        
        # If the moving average of returns is below a certain threshold, stop trading
        if moving_average_return < self.threshold:
            self.Liquidate()

        # Add new prices to the rolling windows
        self.price_windows[self.pairs[0]].Add(data[self.usd_jpy].Close)
        self.price_windows[self.pairs[1]].Add(data[self.gbp_jpy].Close)
        

        # Skip if we don't have enough data
        if not (self.price_windows[self.pairs[0]].IsReady and self.price_windows[self.pairs[1]].IsReady):
            return

        # Calculate the price ratio and z-score for the pair of currencies
        if not all([self.price_windows[sym].IsReady for sym in self.pairs]):
            return

        ratio = self.price_windows[self.pairs[0]][0] / self.price_windows[self.pairs[1]][0]
        self.ratio_windows[self.ratio].Add(ratio)

        window_values = [self.ratio_windows[self.ratio][i] for i in range(self.lookback)]

        mean = np.mean(window_values)
        std = np.std(window_values)

        zscore = (window_values[-1] - mean) / std if std != 0 else 0
        self.zscore_windows[self.ratio].Add(zscore)


        # Trading logic
        holdings_usd_jpy = self.Portfolio[self.usd_jpy].Quantity
        holdings_gbp_jpy = self.Portfolio[self.gbp_jpy].Quantity
      

        # get z score for pairs:
        zscore_USDJPYGBPJPY = self.zscore_windows[self.ratio][0]
      

        # USD/JPY and GBP/JPY trading logic
        if zscore_USDJPYGBPJPY > self.zscore_positive and holdings_usd_jpy <= 0 and holdings_gbp_jpy >= 0:
            # Sell GBPJPY and buy USDJPY
            self.MarketOrder(self.gbp_jpy, -self.CalculateOrderQuantity(self.gbp_jpy, 0.5))
            self.StopMarketOrder(self.gbp_jpy, self.CalculateOrderQuantity(self.gbp_jpy, 0.5), data[self.gbp_jpy].Close * (1 - 0.01))
            self.LimitOrder(self.gbp_jpy, self.CalculateOrderQuantity(self.gbp_jpy, 0.5), data[self.gbp_jpy].Close * (1 + 0.02))
            self.MarketOrder(self.usd_jpy, self.CalculateOrderQuantity(self.usd_jpy, 0.5))
            self.StopMarketOrder(self.usd_jpy, -self.CalculateOrderQuantity(self.usd_jpy, 0.5), data[self.usd_jpy].Close * (1 + 0.01))
            self.LimitOrder(self.usd_jpy, -self.CalculateOrderQuantity(self.usd_jpy, 0.5), data[self.usd_jpy].Close * (1 - 0.02))
        elif zscore_USDJPYGBPJPY < self.zscore_negative and holdings_usd_jpy >= 0 and holdings_gbp_jpy <= 0:
            # Sell USDJPY and buy GBPJPY
            self.SetHoldings(self.gbp_jpy, 0.5)
            self.SetHoldings(self.usd_jpy, -0.5)
        elif abs(zscore_USDJPYGBPJPY) < 0.01:
            # Close positions
            self.Liquidate(self.gbp_jpy)
            self.Liquidate(self.usd_jpy)     