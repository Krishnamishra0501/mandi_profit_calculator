# Mandi-to-Mandi Price Arbitrage Advisor

## 1. Project Overview

**Mandi-to-Mandi Price Arbitrage Advisor** is a decision-support
application designed to help farmers compare nearby agricultural mandis
before deciding where to sell their produce.

The core idea is simple:

> The mandi offering the highest market price is not necessarily the
> mandi that gives the highest net return after transportation, mandi
> charges, and quality-related deductions.

The system is intended to compare nearby mandis using current market
prices, travel distance, transportation cost, mandi charges, and other
deductions, and then calculate the expected **net profit per quintal**.

------------------------------------------------------------------------

## 2. Problem Statement

Farmers may traditionally travel to the nearest mandi without comparing
the economics of alternative mandis.

Existing market-price services can provide current mandi prices, but the
farmer still has to manually consider:

-   Distance to the mandi
-   Transportation cost
-   Mandi commission/fees
-   Quality-related deductions
-   Difference in selling price
-   Historical price movement

This project aims to combine these factors into a single mandi
comparison.

------------------------------------------------------------------------

## 3. Proposed Solution

The intended system flow is:

``` text
Farmer Pincode / Location
          |
          v
Find 5 Nearest Mandis
          |
          v
Fetch Current Mandi Prices
          |
          v
Calculate Road Distance
          |
          v
Calculate Transport Cost
          |
          v
Apply Mandi Fees / Commission
          |
          v
Apply Quality Cut
          |
          v
Calculate Net Profit / Quintal
          |
          v
Rank Mandis
          |
          v
Display 7-Day Price Trends
```

The final application should allow a farmer to compare multiple nearby
mandis instead of considering only the closest mandi.

------------------------------------------------------------------------

# 4. Original Project Requirements

## Mandatory Features

### M1 --- Mandi Locator

Use the farmer's location/pincode to identify the **5 nearest mandis**.

### M2 --- Price Fetcher

For each nearby mandi, retrieve the current/latest available mandi price
for the selected commodity.

The primary price source being used is the official **data.gov.in / eNAM
market-price dataset**.

### M3 --- Profit Calculator

For every mandi calculate:

``` text
Transport Cost
Mandi Fee / Commission
Quality Cut
Net Profit / Quintal
```

and rank the mandis based on calculated net profit.

### M4 --- 7-Day Price Trend

Show the price movement for the selected commodity over the previous 7
days for each nearby mandi.

------------------------------------------------------------------------

# 5. Target Technology Stack

## Frontend

-   Next.js / React
-   Interactive comparison dashboard
-   Charts for 7-day price trends

## Backend

-   Python
-   FastAPI
-   Uvicorn

## Market Data

-   data.gov.in
-   eNAM market-price dataset

## Distance

Planned:

-   Google Routes API / route matrix
-   Actual road distance rather than straight-line distance

## Database

Planned:

-   PostgreSQL

The current prototype uses CSV files for development.

## Deployment

Planned:

-   Frontend: Vercel
-   Backend: Railway

------------------------------------------------------------------------

# 6. Data Sources

## 6.1 Mandi Price Dataset

The project uses the official data.gov.in resource:

**Variety-wise Daily Market Prices Data of Commodity**

Resource ID:

``` text
35985678-0d79-46b4-9ed6-6f13308a1d24
```

Important fields include:

``` text
Arrival_Date
Commodity
Commodity_Code
District
Grade
Market
Max_Price
Min_Price
Modal_Price
State
Variety
```

The project currently uses the `Modal_Price` as the primary market price
for calculations.

## 6.2 Local Price Dataset

A downloaded CSV snapshot is stored at:

``` text
data/mandi_prices.csv
```

This provides a local fallback/development dataset.

## 6.3 Mandi Location Dataset

The current development dataset is:

``` text
data/mandis.csv
```

It contains:

``` text
mandi_name
district
state
latitude
longitude
```

The current dataset contains 36 Maharashtra mandi records and is being
used for development/testing.

**Important:** The current coordinates are a development dataset and
must be verified/replaced with authoritative mandi coordinates before
final evaluation or production deployment.

------------------------------------------------------------------------

# 7. Current Project Structure

``` text
mandi/
│
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── mandi_locator.py
│   │       └── mandi_price.py
│   │
│   ├── .env
│   ├── requirements.txt
│   └── venv/
│
└── data/
    ├── mandi_prices.csv
    └── mandis.csv
```

The following are intentionally excluded from Git:

``` text
backend/venv/
backend/.env
__pycache__/
*.pyc
```

------------------------------------------------------------------------

# 8. What Has Been Completed

## M1 --- Nearest Mandi Locator

Implemented in:

``` text
backend/app/services/mandi_locator.py
```

The service:

1.  Loads `data/mandis.csv`
2.  Accepts latitude and longitude
3.  Calculates distance to every mandi
4.  Sorts mandis by distance
5.  Returns the five nearest mandis

The current prototype uses the **Haversine formula**.

Example test:

``` text
Latitude: 21.1458
Longitude: 79.0882
```

The prototype returned:

``` text
APMC Nagpur       0.00 km
APMC Savner      31.83 km
APMC Katol       53.99 km
APMC Wardha      67.31 km
APMC Hinganghat  71.28 km
```

### Current API

``` http
GET /nearest-mandis
```

Example:

``` text
/nearest-mandis?latitude=21.1458&longitude=79.0882
```

------------------------------------------------------------------------

# 9. Price Fetcher --- Completed

Implemented in:

``` text
backend/app/services/mandi_price.py
```

The service supports:

-   State filtering
-   District filtering
-   Commodity filtering
-   Arrival-date filtering
-   data.gov.in API access
-   Local CSV fallback

The project uses `curl.exe` for the data.gov.in API request because
direct Python HTTP requests previously experienced timeout issues in the
development environment.

The API successfully returned current market records during testing.

Example:

``` text
Commodity: Wheat
Date: 21-09-2026
State: Maharashtra
```

The prototype successfully retrieved mandi records including modal
prices.

------------------------------------------------------------------------

# 10. Mandi Price Comparison --- Completed

Implemented through:

``` http
GET /mandi-prices
```

Example:

``` text
/mandi-prices?latitude=21.1458&longitude=79.0882&commodity=Wheat&arrival_date=21-09-2026
```

The endpoint:

1.  Finds the five nearest mandis
2.  Queries market-price data for each mandi
3.  Matches the mandi with the `Market` field
4.  Extracts the modal price

Example result from testing:

``` text
APMC Nagpur      ₹3425
APMC Savner      ₹2530
APMC Katol       ₹2679
APMC Wardha      ₹2700
APMC Hinganghat  ₹2650
```

------------------------------------------------------------------------

# 11. Arbitrage / Net Profit Calculator --- Completed Prototype

Implemented through:

``` http
GET /arbitrage
```

Example:

``` text
/arbitrage?latitude=21.1458&longitude=79.0882&commodity=Wheat&arrival_date=21-09-2026
```

The current calculation is:

``` text
Transport Cost = Distance × Transport Rate

Commission = Modal Price × Commission %

Quality Cut = Modal Price × Quality Cut %

Net Profit =
Modal Price
- Transport Cost
- Commission
- Quality Cut
```

Current prototype defaults:

``` text
Transport rate = ₹15/km
Commission = 2%
Quality cut = 1%
```

These are configurable query parameters.

### Example tested output

``` text
APMC Nagpur
Modal Price:    ₹3425
Transport:      ₹0
Commission:     ₹68.50
Quality Cut:    ₹34.25
Net Profit:     ₹3322.25

APMC Savner
Modal Price:    ₹2530
Transport:      ₹477.45
Commission:     ₹50.60
Quality Cut:    ₹25.30
Net Profit:     ₹1976.65

APMC Katol
Modal Price:    ₹2679
Transport:      ₹809.85
Commission:     ₹53.58
Quality Cut:    ₹26.79
Net Profit:     ₹1788.78

APMC Wardha
Modal Price:    ₹2700
Transport:      ₹1009.65
Commission:     ₹54.00
Quality Cut:    ₹27.00
Net Profit:     ₹1609.35

APMC Hinganghat
Modal Price:    ₹2650
Transport:      ₹1069.20
Commission:     ₹53.00
Quality Cut:    ₹26.50
Net Profit:     ₹1501.30
```

The results are sorted by net profit.

------------------------------------------------------------------------

# 12. 7-Day Price Trend --- Completed Prototype

Implemented through:

``` http
GET /price-trends
```

Example:

``` text
/price-trends?latitude=21.1458&longitude=79.0882&commodity=Wheat&end_date=21-09-2026
```

The endpoint returns seven daily observations for each of the five
nearest mandis.

Example APMC Nagpur trend:

``` text
15-09-2026 → ₹3275
16-09-2026 → ₹3425
17-09-2026 → ₹3425
18-09-2026 → No record
19-09-2026 → ₹3425
20-09-2026 → No record
21-09-2026 → ₹3425
```

Missing observations are represented as:

``` json
"modal_price": null
```

They should remain missing rather than being treated as zero.

------------------------------------------------------------------------

# 13. Current FastAPI Endpoints

The backend currently exposes:

``` text
GET /
```

Health/status endpoint.

``` text
GET /health
```

Health check.

``` text
GET /prices
```

General market-price query.

Parameters:

``` text
state
district
commodity
arrival_date
```

``` text
GET /nearest-mandis
```

Returns the five nearest mandis.

Parameters:

``` text
latitude
longitude
```

``` text
GET /mandi-prices
```

Returns current prices for the five nearest mandis.

Parameters:

``` text
latitude
longitude
commodity
arrival_date
```

``` text
GET /arbitrage
```

Calculates transport cost, commission, quality cut, net profit, and
ranking.

Parameters:

``` text
latitude
longitude
commodity
arrival_date
transport_rate
commission_percent
quality_cut_percent
```

``` text
GET /price-trends
```

Returns seven-day price trends.

Parameters:

``` text
latitude
longitude
commodity
end_date
```

------------------------------------------------------------------------

# 14. What Still Needs To Be Done

The current implementation is a **working backend prototype**, but it
does not yet fully satisfy the original specification.

The following items are still required.

## 14.1 Pincode / Location Input

Current system requires:

``` text
latitude
longitude
```

The intended user flow is:

``` text
Pincode / Location
        ↓
Coordinates
        ↓
Nearest Mandis
```

A location service needs to be added so the farmer does not have to
manually provide coordinates.

Potential final API:

``` text
GET /location?pincode=440001
```

------------------------------------------------------------------------

# 15. Replace Haversine Distance With Road Distance

The current system uses:

``` text
Haversine distance
```

This is straight-line/geographical distance.

The original specification requires actual transportation distance.

The planned solution is:

``` text
Google Routes API
```

The intended flow:

``` text
Farmer Location
      ↓
Nearest 5 Mandis
      ↓
Google Routes API
      ↓
Road Distance
      ↓
Transport Cost
```

This is important because a truck cannot necessarily travel along a
straight line between two locations.

------------------------------------------------------------------------

# 16. Improve Transport Cost Model

The current prototype uses:

``` text
Distance × ₹15/km
```

This is only a development assumption.

The final model should consider:

-   Quantity being transported
-   Vehicle/load capacity
-   Local transport rate card
-   Potential fixed transportation costs
-   Per-kilometre cost

The final API should accept the farmer's quantity, for example:

``` json
{
    "pincode": "440001",
    "commodity": "Wheat",
    "quantity_quintal": 10
}
```

The transport calculation can then be based on the actual load rather
than treating ₹/km/quintal as a universal rate.

------------------------------------------------------------------------

# 17. Add Mandi-Specific Fees

The current prototype uses:

``` text
Commission = 2%
```

for all mandis.

This is not yet a verified mandi-specific fee model.

The final system should maintain a mandi fee/rate configuration
containing, where available:

``` text
mandi_name
commission
market_fee
other applicable charges
```

The calculation should use the appropriate mandi-specific values.

------------------------------------------------------------------------

# 18. Verify Mandi Coordinates

The current `data/mandis.csv` is a development/testing dataset.

Before final evaluation:

-   Verify mandi names
-   Verify districts
-   Verify coordinates
-   Replace temporary coordinates with authoritative data where possible
-   Ensure the mandi master contains sufficient coverage

This is especially important because the nearest-five calculation
depends directly on these coordinates.

------------------------------------------------------------------------

# 19. Optimize the 7-Day Trend API

The current trend implementation can make:

``` text
5 mandis × 7 dates = up to 35 API queries
```

This is acceptable for a prototype but inefficient.

The final implementation should reduce the number of API requests by:

-   Fetching broader datasets where possible
-   Caching price data
-   Using the local dataset for historical records
-   Avoiding repeated API calls
-   Adding database storage

------------------------------------------------------------------------

# 20. PostgreSQL Integration

The current system primarily uses CSV files.

Planned production architecture:

``` text
PostgreSQL
    |
    ├── Mandis
    ├── Price Records
    ├── Transport Rates
    └── Mandi Fees
```

This will make querying, caching, and historical trends more efficient.

------------------------------------------------------------------------

# 21. Frontend

The frontend has not been implemented yet.

Planned stack:

``` text
Next.js
React
```

The UI should contain:

## Input section

``` text
Pincode / Location
Commodity
Quantity
Date
```

## Mandi comparison

Display:

``` text
Mandi
Distance
Current Price
Transport Cost
Mandi Charges
Quality Cut
Net Profit
Rank
```

## Trend charts

Display a 7-day price chart for each nearby mandi.

The frontend should clearly distinguish:

``` text
Market Price
```

from:

``` text
Net Profit
```

because the highest market price may not produce the highest net return
after costs.

------------------------------------------------------------------------

# 22. Proposed Final User Flow

``` text
                 Farmer
                    |
                    v
          Enter Pincode / Location
                    |
                    v
              Select Crop
                    |
                    v
           Enter Quantity
                    |
                    v
          Find 5 Nearest Mandis
                    |
                    v
        Calculate Actual Road Distance
                    |
                    v
          Fetch Current Prices
                    |
                    v
          Fetch Mandi Charges
                    |
                    v
          Calculate Transport Cost
                    |
                    v
       Calculate Net Profit / Quintal
                    |
                    v
              Rank Mandis
                    |
                    v
         Show 7-Day Price Trends
                    |
                    v
              Farmer Comparison
```

------------------------------------------------------------------------

# 23. Proposed Final API

Instead of requiring the frontend to call many endpoints independently,
the final system can provide a combined analysis endpoint.

Example:

``` http
POST /analyze
```

Request:

``` json
{
    "pincode": "440001",
    "commodity": "Wheat",
    "quantity_quintal": 10
}
```

Response should contain:

``` json
{
    "location": {},
    "mandis": [
        {
            "mandi_name": "",
            "distance_km": 0,
            "current_price": 0,
            "transport_cost": 0,
            "mandi_fee": 0,
            "quality_cut": 0,
            "net_profit": 0,
            "rank": 1,
            "price_trend": []
        }
    ]
}
```

This would make the frontend much simpler.

------------------------------------------------------------------------

# 24. Error Handling To Add

The final backend should handle:

-   Invalid pincode
-   Location service failure
-   Mandi data unavailable
-   Price unavailable
-   Missing historical price
-   Google Routes API failure
-   data.gov.in timeout
-   Invalid commodity
-   Invalid quantity
-   Invalid date
-   API rate limits

The system should return useful error messages instead of generic
`500 Internal Server Error` responses wherever possible.

------------------------------------------------------------------------

# 25. Performance Target

Original evaluation target:

``` text
API response < 3 seconds
```

The current implementation has not yet been optimized or benchmarked
against this requirement.

The final system should use:

-   Cached mandi data
-   Cached price data
-   Efficient API calls
-   Database queries
-   Reduced external API calls

to approach the target.

------------------------------------------------------------------------

# 26. Accuracy Evaluation

Original evaluation requirement:

``` text
Profit calculation accuracy within 5%
on 10 real scenarios
```

A final evaluation set should contain at least 10 real farmer/mandi
scenarios.

For every scenario compare:

``` text
Expected / verified profit
vs
System calculated profit
```

and calculate the error percentage.

------------------------------------------------------------------------

# 27. Deployment Plan

## Frontend

``` text
Vercel
```

## Backend

``` text
Railway
```

## Database

``` text
PostgreSQL
```

Production environment variables should be configured through the
deployment platform and must not be committed to Git.

------------------------------------------------------------------------

# 28. API Documentation

FastAPI automatically provides:

``` text
/docs
```

and:

``` text
/redoc
```

while the server is running.

Example:

``` text
http://127.0.0.1:8000/docs
```

The final project should additionally document:

-   API parameters
-   Request examples
-   Response examples
-   Error responses
-   Authentication/API-key requirements
-   Data sources

------------------------------------------------------------------------

# 29. Git / Repository

Git repository:

``` text
https://github.com/Krishnamishra0501/mandi_profit_calculator
```

The project is being maintained with Git.

The current checkpoint includes:

``` text
backend/app/main.py
backend/app/services/mandi_locator.py
backend/app/services/mandi_price.py
backend/requirements.txt
data/mandi_prices.csv
data/mandis.csv
.gitignore
```

Sensitive files such as:

``` text
backend/.env
backend/venv/
```

are excluded from Git.

------------------------------------------------------------------------

# 30. Current Development Status

## Completed

-   [x] FastAPI backend setup
-   [x] Virtual environment
-   [x] data.gov.in price integration
-   [x] CSV price fallback
-   [x] Mandi location dataset
-   [x] Nearest-five mandi calculation
-   [x] `/nearest-mandis`
-   [x] `/prices`
-   [x] `/mandi-prices`
-   [x] Current modal-price retrieval
-   [x] Transport-cost prototype
-   [x] Commission calculation prototype
-   [x] Quality-cut calculation prototype
-   [x] Net-profit calculation
-   [x] Profit ranking
-   [x] `/arbitrage`
-   [x] Seven-day trend retrieval
-   [x] `/price-trends`
-   [x] Git repository setup
-   [x] `.gitignore`

## In Progress / Remaining

-   [ ] Pincode/location service
-   [ ] Authoritative mandi coordinates
-   [ ] Google Routes API
-   [ ] Actual road-distance calculation
-   [ ] Real transport rate card
-   [ ] Quantity-aware transport model
-   [ ] Mandi-specific fees
-   [ ] PostgreSQL
-   [ ] API optimization/caching
-   [ ] Combined `/analyze` endpoint
-   [ ] Next.js frontend
-   [ ] Interactive 7-day charts
-   [ ] Error handling improvements
-   [ ] Performance benchmarking
-   [ ] 10-scenario accuracy evaluation
-   [ ] Deployment
-   [ ] API documentation
-   [ ] Final report
-   [ ] 3-minute project demonstration

------------------------------------------------------------------------

# 31. Important Current Limitations

The current implementation should be considered a **working prototype**,
not the final production implementation.

The most important limitations are:

1.  Coordinates are currently development data.
2.  Distance is currently straight-line Haversine distance.
3.  Transport rate is currently a configurable assumption.
4.  Commission and quality-cut percentages are currently configurable
    assumptions rather than verified mandi-specific rates.
5.  Pincode-to-location functionality has not yet been implemented.
6.  Quantity/load is not yet part of the transport calculation.
7.  PostgreSQL has not yet been integrated.
8.  Frontend has not yet been implemented.
9.  Seven-day trends can currently require many external API requests.
10. The final response-time target has not yet been benchmarked.

These limitations should be resolved before claiming the complete
solution satisfies the original evaluation criteria.

------------------------------------------------------------------------

# 32. Development Roadmap

### Phase 1 --- Backend Prototype

Completed:

``` text
Mandi data
    ↓
Nearest 5
    ↓
Current prices
    ↓
Profit calculation
    ↓
Ranking
    ↓
7-day trends
```

### Phase 2 --- Specification Compliance

Next:

``` text
Pincode
   ↓
Location
   ↓
Verified mandi coordinates
   ↓
Road distance
   ↓
Real transport model
   ↓
Mandi-specific charges
```

### Phase 3 --- Data & Performance

Then:

``` text
PostgreSQL
Caching
API optimization
Error handling
```

### Phase 4 --- Frontend

Then:

``` text
Next.js
    ↓
Input form
    ↓
Mandi comparison
    ↓
Profit ranking
    ↓
Trend charts
```

### Phase 5 --- Deployment & Evaluation

Finally:

``` text
Vercel
+
Railway
+
PostgreSQL
+
10 real scenarios
+
<3 second target
+
Documentation
+
Demo
+
Report
```

------------------------------------------------------------------------

# 33. Project Goal

The final application should answer one practical question for a farmer:

> **"After considering price, distance, transportation, mandi charges,
> and other deductions, which nearby mandi gives me the calculated
> highest net return per quintal?"**

The system should provide the underlying numbers transparently so that
the farmer can understand **why** the calculated net return differs
between mandis.

------------------------------------------------------------------------

## Current Status

**Backend prototype: working**

**Specification-compliant production MVP: not yet complete**

**Next priority: Pincode/location → verified mandi locations → Google
road distance → realistic transport and mandi-fee model.**
