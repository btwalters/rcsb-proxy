from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/search")
async def search_rcsb(req: Request):
    body = await req.json()
    query = body.get("query", "").strip()
    max_results = int(body.get("max_results", 10))

    print(f"🔍 Searching RCSB for: '{query}' (max: {max_results})")

    if not query:
        return JSONResponse(status_code=400, content={"error": "Query term is missing."})

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

    try:
        r = requests.post("https://search.rcsb.org/rcsbsearch/v2/query?json=", json=search_body)
        r.raise_for_status()
        response_json = r.json()

        print(f"📥 RCSB response status: {r.status_code}")
        print(f"📦 Full JSON received: {response_json}")

        result_set = response_json.get("result_set", [])
        pdb_ids = [res.get("identifier") for res in result_set if "identifier" in res]

        if not pdb_ids:
            print("⚠️ No PDB IDs found.")
            return JSONResponse(status_code=200, content={
                "pdb_ids": [],
                "download_links": [],
                "message": f"No results found for query: '{query}'"
            })

        download_links = [f"https://files.rcsb.org/download/{pid}.pdb" for pid in pdb_ids]

        return JSONResponse(content={
            "pdb_ids": pdb_ids,
            "download_links": download_links
        })

    except Exception as e:
        print(f"❌ Error during request: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to fetch results from RCSB."})
