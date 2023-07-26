# OANDA API Documentation

## REST API

| Environment | URL | Authentication | Description |
|-------------|-----|----------------|-------------|
| fxTrade Practice | https://api-fxpractice.oanda.com | Required. [Details Here](#) | A stable environment; recommended for testing with your fxTrade Practice account and your personal access token. |
| fxTrade | https://api-fxtrade.oanda.com | Required. [Details Here](#) | A stable environment; recommended for production-ready code to execute with your fxTrade account and your personal access token. |

## Streaming API

| Environment | URL | Authentication | Description |
|-------------|-----|----------------|-------------|
| fxTrade Practice | https://stream-fxpractice.oanda.com/ | Required. [Details Here](#) | A stable environment; recommended for testing with your fxTrade Practice account and your personal access token. |
| fxTrade | https://stream-fxtrade.oanda.com/ | Required. [Details Here](#) | A stable environment; recommended for production-ready code to execute with your fxTrade account and your personal access token. |

## Request and Response Details

All requests with a body require `Content-Type: application/json` unless specified otherwise.

All responses will have `Content-Type: application/json` unless specified otherwise.

## Rate Limiting

### REST API

120 requests per second. Excess requests will receive HTTP 429 error. This restriction is applied against the requesting IP address.

### Streaming API

20 active streams. Requests above this threshold will be rejected. This restriction is applied against the requesting IP address.

## Connection Limiting

Client is allowed to make no more than 2 new connections per second. Excess connections will be rejected. For more details on making persistent connections, please refer to the Best Practices page.

## Order Endpoints

### POST/v3/accounts/{accountID}/orders

Create an Order for an Account

### GET/v3/accounts/{accountID}/orders

Get a list of Orders for an Account

### GET/v3/accounts/{accountID}/pendingOrders

List all pending Orders in an Account

### GET/v3/accounts/{accountID}/orders/{orderSpecifier}

Get details for a single Order in an Account

### PUT/v3/accounts/{accountID}/orders/{orderSpecifier}

Replace an Order in an Account by simultaneously cancelling it and creating a replacement Order

### PUT/v3/accounts/{accountID}/orders/{orderSpecifier}/cancel

Cancel a pending Order in an Account

### PUT/v3/accounts/{accountID}/orders/{orderSpecifier}/clientExtensions

Update the Client Extensions for an Order in an Account. Do not set, modify, or delete clientExtensions if your account is associated with MT4.

## Pricing Endpoints

### GET/v3/accounts/{accountID}/candles/latest

Get dancing bears and most recently completed candles within an Account for specified combinations of instrument, granularity, and price component.

### GET/v3/accounts/{accountID}/pricing

Get pricing information for a specified list of Instruments within an Account.

### GET/v3/accounts/{accountID}/pricing/stream

Get a stream of Account Prices starting from when the request is made. This pricing stream does not include every single price created for the Account, but instead will provide at most 4 prices per second (every 250 milliseconds) for each instrument being requested. If more than one price is created for an instrument during the 250 millisecond window, only the price in effect at the end of the window is sent. This means that during periods of rapid price movement, subscribers to this stream will not be sent every price. Pricing windows for different connections to the price stream are not all aligned in the same way (i.e. they are not all aligned to the top of the second). This means that during periods of rapid price movement, different subscribers may observe different prices depending on their alignment.

Note: This endpoint is served by the streaming URLs.

### GET/v3/accounts/{accountID}/instruments/{instrument}/candles

Fetch candlestick data for an instrument.
