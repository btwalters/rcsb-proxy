from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/search")
async def search_rcsb(req: Request):
    try:
        body = await req.json()
        query = body.get("query", "").strip()
        max_results = int(body.get("max_results", 10))

        if not query:
            return JSONResponse(status_code=400, content={"error": "Query term is missing."})

        # Construct valid search body (minimal and RCSB-compliant)
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
                "results_content_type": ["experimental"],
                "results_verbosity": "compact",
                "rows": max_results
            }
        }

        print(f"📤 Sending to RCSB:\n{search_body}")

        r = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json=search_body)
        r.raise_for_status()

        data = r.json()
        result_set = data.get("result_set", [])
        print(f"📦 Received {len(result_set)} results from RCSB")

        pdb_ids = [res.get("identifier") for res in result_set if res.get("identifier")]
        download_links = [f"https://files.rcsb.org/download/{pid}.pdb" for pid in pdb_ids]

        return JSONResponse(content={
            "pdb_ids": pdb_ids,
            "download_links": download_links
        })

    except Exception as e:
        print(f"❌ Error during RCSB fetch: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to fetch results from RCSB."})
