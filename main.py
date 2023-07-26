import asyncio
from data_layer.data_feed import DataFetcher, OandaData, OandaAuth, get_unix_timestamp
import datetime
from execution_layer.execution import Execution

# Define the instruments
instruments = ['GBP_JPY', 'USD_JPY']  # Add more instrument names as needed

# fill MongoDB with historical data for all instruments
for instrument in instruments:
    oandadata = OandaData(OandaAuth(), instrument)
    oandadata.get_historical_data(instrument=instrument, from_time=get_unix_timestamp(3), to_time=get_unix_timestamp(0))

# Initialize DataFetchers for each instrument
data_fetchers = [DataFetcher(instrument) for instrument in instruments]

# Initialize an Execution object
execution = Execution(auth=OandaAuth(), instruments=instruments)

# Define an asynchronous function to fetch real-time data and execute trades
# Define an asynchronous function to fetch real-time data and execute trades
async def main():
    while True:
        # Fetch real-time data for each instrument concurrently
        fetch_tasks = [asyncio.create_task(df.fetch_real_time_data()) for df in data_fetchers]
        # Execute trades based on the fetched data
        exec_task = asyncio.create_task(execution.get_candle_data())

        # Wait for all tasks to complete
        await asyncio.sleep(10)  # Wait for some time before the next iteration


# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
