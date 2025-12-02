"""
IQVIA Market Data Tool
Queries market data from database for molecule/region analysis.
"""
import json
from typing import Optional, List
from crewai.tools import tool
from pathlib import Path


def _load_iqvia_data() -> list:
    """Load IQVIA market data from database, fallback to JSON."""
    try:
        from ..database.db import get_db_session
        from ..database.models import MarketData
        
        with get_db_session() as db:
            records = db.query(MarketData).all()
            if records:
                return [
                    {
                        "molecule": r.molecule,
                        "region": r.region,
                        "therapy_area": r.therapy_area,
                        "indication": r.indication,
                        "market_size_usd_mn": r.market_size_usd_mn,
                        "cagr_percent": r.cagr_percent,
                        "top_competitors": r.top_competitors or [],
                        "generic_penetration": r.generic_penetration,
                        "patient_burden": r.patient_burden,
                        "competition_level": r.competition_level
                    }
                    for r in records
                ]
    except Exception:
        pass
    
    # Fallback to JSON file
    data_path = Path(__file__).resolve().parent.parent.parent / "mock_data" / "iqvia_market_data.json"
    if data_path.exists():
        with open(data_path, "r") as f:
            return json.load(f)
    return []


@tool("Query IQVIA Market Data")
def query_iqvia_market(molecule: Optional[str] = None, region: Optional[str] = None, therapy_area: Optional[str] = None) -> str:
    """
    Query IQVIA market data for pharmaceutical market intelligence.
    
    Args:
        molecule: Name of the molecule/drug to search for (e.g., 'Pembrolizumab', 'Sitagliptin')
        region: Geographic region to filter by (e.g., 'India', 'US', 'Global')
        therapy_area: Therapeutic area to filter by (e.g., 'Respiratory', 'Oncology', 'Diabetes')
    
    Returns:
        Market data including market size, CAGR, competitors, and generic penetration.
    """
    try:
        data = _load_iqvia_data()
        results = []
        
        for entry in data:
            # Filter by molecule if provided
            if molecule and molecule.lower() not in entry.get("molecule", "").lower():
                continue
            # Filter by region if provided
            if region and region.lower() not in entry.get("region", "").lower():
                continue
            # Filter by therapy area if provided
            if therapy_area and therapy_area.lower() not in entry.get("therapy_area", "").lower():
                continue
            results.append(entry)
        
        if not results:
            return f"No IQVIA market data found for molecule='{molecule}', region='{region}', therapy_area='{therapy_area}'"
        
        # Format results
        output = []
        for r in results:
            output.append(
                f"**{r['molecule']}** ({r['region']}):\n"
                f"  - Therapy Area: {r.get('therapy_area', 'N/A')}\n"
                f"  - Market Size: ${r['market_size_usd_mn']}M USD\n"
                f"  - CAGR: {r['cagr_percent']}%\n"
                f"  - Top Competitors: {', '.join(r['top_competitors'])}\n"
                f"  - Generic Penetration: {r['generic_penetration']}\n"
                f"  - Patient Burden: {r.get('patient_burden', 'N/A')}\n"
                f"  - Competition Level: {r.get('competition_level', 'N/A')}"
            )
        
        return "\n\n".join(output)
    
    except Exception as e:
        return f"Error querying IQVIA data: {str(e)}"


@tool("Find Low Competition Markets")
def find_low_competition_markets(therapy_area: str, region: str = "India") -> str:
    """
    Find markets with low competition and high patient burden - ideal for whitespace analysis.
    
    Args:
        therapy_area: Therapeutic area to analyze (e.g., 'Respiratory', 'Oncology')
        region: Geographic region to filter (default: 'India')
    
    Returns:
        List of molecules with low competition and high patient burden.
    """
    try:
        data = _load_iqvia_data()
        opportunities = []
        
        for entry in data:
            # Check therapy area match
            if therapy_area.lower() not in entry.get("therapy_area", "").lower():
                continue
            # Check region match
            if region.lower() not in entry.get("region", "").lower():
                continue
            # Check for low competition
            competition = entry.get("competition_level", entry.get("generic_penetration", ""))
            if competition.lower() in ["low", "medium"]:
                opportunities.append({
                    "molecule": entry["molecule"],
                    "indication": entry.get("indication", entry.get("therapy_area")),
                    "market_size": entry["market_size_usd_mn"],
                    "cagr": entry["cagr_percent"],
                    "competition": competition,
                    "patient_burden": entry.get("patient_burden", "N/A")
                })
        
        if not opportunities:
            return f"No low competition opportunities found in {therapy_area} for {region}"
        
        # Sort by CAGR (highest first)
        opportunities.sort(key=lambda x: x["cagr"], reverse=True)
        
        output = [f"**Whitespace Opportunities in {therapy_area} ({region}):**\n"]
        for opp in opportunities:
            output.append(
                f"- **{opp['molecule']}** ({opp['indication']})\n"
                f"  Market: ${opp['market_size']}M | CAGR: {opp['cagr']}% | "
                f"Competition: {opp['competition']} | Patient Burden: {opp['patient_burden']}"
            )
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error finding opportunities: {str(e)}"
