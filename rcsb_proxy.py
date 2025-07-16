from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/search")
async def search_rcsb(req: Request):
    body = await req.json()
    query = body.get("query")
    max_results = body.get("max_results", 10)

    print(f"🔍 Searching RCSB for: '{query}' with max_results={max_results}")

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

    response = requests.post("https://search.rcsb.org/rcsbsearch/v2/query?json=", json=search_body)
    print(f"📥 RCSB response status: {response.status_code}")
    print(f"📦 Raw RCSB result: {response.text[:500]}")  # Limit output

    try:
        data = response.json()
        pdb_ids = [res["identifier"] for res in data.get("result_set", [])]
    except Exception as e:
        print(f"⚠️ Error parsing response: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to parse RCSB response"})

    download_links = [f"https://files.rcsb.org/download/{pid}.pdb" for pid in pdb_ids]

    return JSONResponse(content={
        "pdb_ids": pdb_ids,
        "download_links": download_links
    })
