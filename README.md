# pairtrader
This is a trading system for Oanda. The data layer is responsible for filling the MongoDB instance with historical data 
and also continuously filling it with real-time data. The execution layer creates a rolling window based on the latest data
and calculates indicators (the z-score) and makes trading decisions based on that. 

The code for backtesting on QuantConnect is in /strategy
