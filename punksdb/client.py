import requests


class DB:

    def __init__(self):
        self.url = "http://us.monkey-network.xyz:5002"
        self.key = "YOUR_PUNKSDB_KEY"

    def _request(self, action, **data):

        response = requests.post(
            f"{self.url}/request",
            json={
                "action": action,
                **data
            },
            headers={
                "X-PunksDB-Key": self.key
            },
            timeout=10
        )

        response.raise_for_status()

        result = response.json()

        if not result.get("success"):
            raise RuntimeError(
                result.get("error", "PunksDB request failed")
            )

        return result.get("result")


    def create_table(self, table, columns):
        return self._request(
            "create_table",
            table=table,
            columns=columns
        )


    def insert(self, table, data):
        return self._request(
            "insert",
            table=table,
            data=data
        )


    def fetchone(self, table, where=None, params=()):
        return self._request(
            "fetchone",
            table=table,
            where=where,
            params=list(params)
        )


    def fetchall(self, table, where=None, params=()):
        return self._request(
            "fetchall",
            table=table,
            where=where,
            params=list(params)
        )


    def update(self, table, data, where, params=()):
        return self._request(
            "update",
            table=table,
            data=data,
            where=where,
            params=list(params)
        )


    def delete(self, table, where, params=()):
        return self._request(
            "delete",
            table=table,
            where=where,
            params=list(params)
        )


    def exists(self, table, where, params=()):
        return self._request(
            "exists",
            table=table,
            where=where,
            params=list(params)
        )
