from typing import List, Dict
import clickhouse_connect


def get_clickhouse_client():
    """
    Create and return a ClickHouse client.
    This version uses explicit credentials to avoid environment
    variable mismatches inside Docker containers.
    """

    client = clickhouse_connect.get_client(
        host="clickhouse",
        port=8123,
        username="default",
        password="admin123",
        database="default",
    )

    return client


def insert_batch(rows: List[Dict], table_name: str = "currency") -> None:
    """
    Insert prepared rows into ClickHouse.
    """

    if not rows:
        print("No rows to insert into ClickHouse.")
        return

    client = get_clickhouse_client()

    data = [
        [
            row["id"],
            row["date"],
            row["usd"],
            row["euro"],
            row["created"],
            row["updated"],
        ]
        for row in rows
    ]

    client.insert(
        table=table_name,
        data=data,
        column_names=["id", "date", "usd", "euro", "created", "updated"],
    )

    print(f"Inserted {len(rows)} rows into ClickHouse table '{table_name}'.")


def check_clickhouse_connection() -> bool:
    """
    Simple connection test for ClickHouse.
    """

    client = get_clickhouse_client()
    result = client.query("SELECT 1")

    return result.result_rows[0][0] == 1


if __name__ == "__main__":
    try:
        if check_clickhouse_connection():
            print("ClickHouse connection successful.")
    except Exception as error:
        print(f"ClickHouse connection failed: {error}")
        raise