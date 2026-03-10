import uuid
from datetime import datetime
from typing import List, Dict


def transform_currency_data(raw_data: List[Dict]) -> List[Dict]:
    """
    Transform raw ECB data into rows ready for ClickHouse insertion.
    """

    created_at = datetime.utcnow()

    transformed = []

    for item in raw_data:
        transformed.append(
            {
                "id": str(uuid.uuid4()),
                "date": datetime.strptime(item["date"], "%Y-%m-%d").date(),
                "usd": 1.0,
                "euro": float(item["euro"]),
                "created": created_at,
                "updated": None,
            }
        )

    return transformed