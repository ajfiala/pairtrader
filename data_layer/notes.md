## GET /v3/accounts/{accountID}/instruments/{instrument}/candles

Fetch candlestick data for an instrument.

### Request

#### Request Parameters

| Name | Located In | Type | Description | Default | Constraints |
| ---- | ---------- | ---- | ----------- | ------- | ----------- |
| Authorization | header | string | The authorization bearer token previously obtained by the client | | Required |
| Accept-Datetime-Format | header | AcceptDatetimeFormat | Format of DateTime fields in the request and response | | |
| accountID | path | AccountID | Account Identifier | | Required |
| instrument | path | InstrumentName | Name of the Instrument | | Required |
| price | query | PricingComponent | The Price component(s) to get candlestick data for | M | |
| granularity | query | CandlestickGranularity | The granularity of the candlesticks to fetch | S5 | |
| count | query | integer | The number of candlesticks to return in the response. Count should not be specified if both the start and end parameters are provided, as the time range combined with the granularity will determine the number of candlesticks to return | 500 | Maximum: 5000 |
| from | query | DateTime | The start of the time range to fetch candlesticks for | | |
| to | query | DateTime | The end of the time range to fetch candlesticks for | | |
| smooth | query | boolean | A flag that controls whether the candlestick is “smoothed” or not. A smoothed candlestick uses the previous candle’s close price as its open price, while an unsmoothed candlestick uses the first price from its time range as its open price | False | |
| includeFirst | query | boolean | A flag that controls whether the candlestick that is covered by the from time should be included in the results. This flag enables clients to use the timestamp of the last completed candlestick received to poll for future candlesticks but avoid receiving the previous candlestick repeatedly | True | |
| dailyAlignment | query | integer | The hour of the day (in the specified timezone) to use for granularities that have daily alignments | 17 | Minimum: 0, Maximum: 23 |
| alignmentTimezone | query | string | The timezone to use for the dailyAlignment parameter. Candlesticks with daily alignment will be aligned to the dailyAlignment hour within the alignmentTimezone. Note that the returned times will still be represented in UTC | America/New_York | |
| weeklyAlignment | query | WeeklyAlignment | The day of the week used for granularities that have weekly alignment | Friday | |
| units | query | DecimalNumber | The number of units used to calculate the volume-weighted average bid and ask prices in the returned candles | 1 | |
