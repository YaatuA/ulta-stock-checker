# Ulta Stock Checker

This service checks the availability of a specific Ulta product every 15 minutes and sends a push notification via Pushover when it is back in stock.

## Setup

1. Create a Pushover account and application.
2. Save your `PRODUCT_URL`, `PUSHOVER_USER_KEY`, and `PUSHOVER_API_TOKEN`.
3. Deploy using Render as a cron job scheduled every 15 minutes.

## Local Testing

Create a `.env` file with:         
PRODUCT_URL=https://www.ulta.com/p/your-product-url<br>
PUSHOVER_USER_KEY=your-user-key-here     
PUSHOVER_API_TOKEN=your-api-token-here     
