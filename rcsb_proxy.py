from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.get("/test")
def test_rcsb():
    search_body = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "value": "insulin"
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 5
            }
        }
    }

    try:
        r = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json=search_body)
        r.raise_for_status()
        result = r.json()
        pdb_ids = [res["identifier"] for res in result.get("result_set", [])]
        return JSONResponse(content={"pdb_ids": pdb_ids})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
