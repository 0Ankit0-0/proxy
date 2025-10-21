from fastapi import APIRouter

router = APIRouter()

@router.post("/run")
async def run_analysis():
    """Endpoint to run analysis on the collected log data(offline).
    Later: implement analysis logic using analysis_service and return the results.
    """ 
    return {"status": "Analysis functionality not implemented yet"}

@router.get("/results")
async def get_analysis_results():
    """Endpoint to get analysis results(offline).
    Later: retrieve analysis results from duckdb and return them.
    """ 
    return {"results": [], "status": "Results functionality not implemented yet"}