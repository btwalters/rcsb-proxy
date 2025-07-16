from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/search")
async def search_rcsb(req: Request):
    body = await req.json()
    query = body.get("query")
    max_results = body.get("max_results", 10)

    search_body = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "value": query
            }
        },
        "return_type": "entry",
        "request_options": {
            "pager": {
                "start": 0,
                "rows": max_results
            }
        }
    }

    r = requests.post("https://search.rcsb.org/rcsbsearch/v2/query?json=", json=search_body)
    pdb_ids = [res["identifier"] for res in r.json().get("result_set", [])]
    download_links = [f"https://files.rcsb.org/download/{pid}.pdb" for pid in pdb_ids]

    return JSONResponse(content={
        "pdb_ids": pdb_ids,
        "download_links": download_links
    })
