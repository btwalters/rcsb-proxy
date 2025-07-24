from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests, logging, json

logging.basicConfig(level=logging.INFO)
app = FastAPI()

RCSB_SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"

@app.post("/search")
async def proxy_search(req: Request):
    """Simple pass-through proxy to the RCSB structured search service."""
    query_body = await req.json()
    logging.info("Incoming query from GPT:\n%s", json.dumps(query_body, indent=2)[:800])

    try:
        resp = requests.post(RCSB_SEARCH_URL, json=query_body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        pdb_ids = [item.get("identifier") for item in data.get("result_set", []) if item.get("identifier")]
        download_links = [f"https://files.rcsb.org/download/{pid}.pdb" for pid in pdb_ids]
        return JSONResponse(content={"pdb_ids": pdb_ids, "download_links": download_links})
    except Exception as e:
        logging.exception("Proxy error")
        return JSONResponse(status_code=500, content={"error": str(e)})
