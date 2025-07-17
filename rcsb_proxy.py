from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

@app.post("/search")
async def proxy_rcsb_query(req: Request):
    query_body = await req.json()
    try:
        r = requests.post("https://search.rcsb.org/rcsbsearch/v2/query", json=query_body)
        r.raise_for_status()
        result = r.json()
        pdb_ids = [res["identifier"] for res in result.get("result_set", [])]
        download_links = [f"https://files.rcsb.org/download/{pid}.pdb" for pid in pdb_ids]
        return JSONResponse(content={"pdb_ids": pdb_ids, "download_links": download_links})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)}})
