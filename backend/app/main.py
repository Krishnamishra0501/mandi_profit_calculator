from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta

from app.services.mandi_price import get_prices
from app.services.mandi_locator import get_nearest_mandis


app = FastAPI(
    title="Mandi-to-Mandi Price Arbitrage Advisor",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Mandi Arbitrage Advisor API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/prices")
async def prices(
    state: str,
    district: str | None = None,
    commodity: str | None = None,
    arrival_date: str | None = None
):
    try:
        data = await get_prices(
            state=state,
            district=district,
            commodity=commodity,
            arrival_date=arrival_date
        )

        return {
            "count": len(data),
            "records": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/nearest-mandis")
def nearest_mandis(
    latitude: float,
    longitude: float
):
    try:
        data = get_nearest_mandis(
            latitude,
            longitude
        )

        return {
            "count": len(data),
            "mandis": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/mandi-prices")
async def mandi_prices(
    latitude: float,
    longitude: float,
    commodity: str,
    arrival_date: str
):
    try:
        mandis = get_nearest_mandis(
            latitude,
            longitude
        )

        results = []

        for mandi in mandis:
            prices = await get_prices(
                state=mandi["state"],
                district=mandi["district"],
                commodity=commodity,
                arrival_date=arrival_date
            )

            mandi_prices = []

            for price in prices:
                market = str(
                    price.get("Market", "")
                ).strip().lower()

                mandi_name = str(
                    mandi["mandi_name"]
                ).strip().lower()

                if (
                    market == mandi_name
                    or mandi_name in market
                    or market in mandi_name
                ):
                    mandi_prices.append(price)

            modal_prices = []

            for price in mandi_prices:
                try:
                    modal_prices.append(
                        float(price["Modal_Price"])
                    )
                except:
                    pass

            if modal_prices:
                modal_price = max(modal_prices)
            else:
                modal_price = None

            results.append({
                "mandi_name": mandi["mandi_name"],
                "district": mandi["district"],
                "distance_km": mandi["distance_km"],
                "commodity": commodity,
                "modal_price": modal_price,
                "records_found": len(mandi_prices)
            })

        return {
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/arbitrage")
async def arbitrage(
    latitude: float,
    longitude: float,
    commodity: str,
    arrival_date: str,
    transport_rate: float = 15,
    commission_percent: float = 2,
    quality_cut_percent: float = 1
):
    try:
        mandis = get_nearest_mandis(
            latitude,
            longitude
        )

        results = []

        for mandi in mandis:
            prices = await get_prices(
                state=mandi["state"],
                district=mandi["district"],
                commodity=commodity,
                arrival_date=arrival_date
            )

            mandi_prices = []

            for price in prices:
                market = str(
                    price.get("Market", "")
                ).strip().lower()

                mandi_name = str(
                    mandi["mandi_name"]
                ).strip().lower()

                if (
                    market == mandi_name
                    or mandi_name in market
                    or market in mandi_name
                ):
                    mandi_prices.append(price)

            modal_prices = []

            for price in mandi_prices:
                try:
                    modal_prices.append(
                        float(price["Modal_Price"])
                    )
                except:
                    pass

            if not modal_prices:
                results.append({
                    "mandi_name": mandi["mandi_name"],
                    "district": mandi["district"],
                    "distance_km": mandi["distance_km"],
                    "commodity": commodity,
                    "modal_price": None,
                    "transport_cost": None,
                    "commission": None,
                    "quality_cut": None,
                    "net_profit": None
                })

                continue

            modal_price = max(modal_prices)

            transport_cost = (
                mandi["distance_km"] * transport_rate
            )

            commission = (
                modal_price * commission_percent / 100
            )

            quality_cut = (
                modal_price * quality_cut_percent / 100
            )

            net_profit = (
                modal_price
                - transport_cost
                - commission
                - quality_cut
            )

            results.append({
                "mandi_name": mandi["mandi_name"],
                "district": mandi["district"],
                "distance_km": mandi["distance_km"],
                "commodity": commodity,
                "modal_price": round(modal_price, 2),
                "transport_cost": round(transport_cost, 2),
                "commission": round(commission, 2),
                "quality_cut": round(quality_cut, 2),
                "net_profit": round(net_profit, 2)
            })

        results.sort(
            key=lambda x: (
                x["net_profit"]
                if x["net_profit"] is not None
                else -1
            ),
            reverse=True
        )

        for rank, result in enumerate(results, start=1):
            result["rank"] = rank

        return {
            "commodity": commodity,
            "arrival_date": arrival_date,
            "transport_rate_per_km": transport_rate,
            "commission_percent": commission_percent,
            "quality_cut_percent": quality_cut_percent,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/price-trends")
async def price_trends(
    latitude: float,
    longitude: float,
    commodity: str,
    end_date: str
):
    try:
        mandis = get_nearest_mandis(
            latitude,
            longitude
        )

        end = datetime.strptime(
            end_date.strip(),
            "%d-%m-%Y"
        )

        dates = []

        for i in range(6, -1, -1):
            date = end - timedelta(days=i)

            dates.append(
                date.strftime("%d-%m-%Y")
            )

        results = []

        for mandi in mandis:

            trend = []

            for date in dates:

                prices = await get_prices(
                    state=mandi["state"],
                    district=mandi["district"],
                    commodity=commodity,
                    arrival_date=date
                )

                modal_prices = []

                for price in prices:

                    market = str(
                        price.get("Market", "")
                    ).strip().lower()

                    mandi_name = str(
                        mandi["mandi_name"]
                    ).strip().lower()

                    if (
                        market == mandi_name
                        or mandi_name in market
                        or market in mandi_name
                    ):
                        try:
                            modal_prices.append(
                                float(
                                    price["Modal_Price"]
                                )
                            )
                        except:
                            pass

                if modal_prices:

                    modal_price = max(
                        modal_prices
                    )

                    trend.append({
                        "date": date,
                        "modal_price": modal_price
                    })

                else:

                    trend.append({
                        "date": date,
                        "modal_price": None
                    })

            results.append({
                "mandi_name": mandi["mandi_name"],
                "district": mandi["district"],
                "commodity": commodity,
                "trend": trend
            })

        return {
            "commodity": commodity,
            "end_date": end_date,
            "days": 7,
            "mandis": results
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="end_date must be in DD-MM-YYYY format"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )