"""
Patent Landscape Tool
Queries USPTO mock data for patent expiry and FTO analysis.
"""
import json
from datetime import datetime
from crewai.tools import tool
from pathlib import Path


def _load_patent_data() -> list:
    """Load USPTO mock data from JSON file."""
    data_path = Path(__file__).resolve().parent.parent.parent / "mock_data" / "uspto_patents.json"
    with open(data_path, "r") as f:
        return json.load(f)


@tool("Query Patent Data")
def query_patents(molecule: str) -> str:
    """
    Query patent data for a specific molecule including expiry dates and status.
    
    Args:
        molecule: Name of the molecule/drug to search for patent information.
    
    Returns:
        Patent details including patent numbers, types, expiry dates, and status.
    """
    try:
        data = _load_patent_data()
        
        # Find matching molecule
        result = None
        for entry in data:
            if molecule.lower() in entry.get("molecule", "").lower():
                result = entry
                break
        
        if not result:
            return f"No patent data found for molecule: {molecule}"
        
        # Format output
        output = [f"**Patent Landscape for {result['molecule']}:**\n"]
        
        for patent in result.get("patents", []):
            expiry_date = patent["expiry_date"]
            status = patent["status"]
            
            # Calculate days until expiry
            try:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                today = datetime.now()
                days_remaining = (expiry - today).days
                
                if days_remaining < 0:
                    time_info = f"Expired {abs(days_remaining)} days ago"
                elif days_remaining < 365:
                    time_info = f"Expires in {days_remaining} days (< 1 year)"
                else:
                    years = days_remaining // 365
                    time_info = f"Expires in ~{years} years"
            except:
                time_info = "Date parsing error"
            
            output.append(
                f"- **{patent['patent_number']}** ({patent['type']})\n"
                f"  Status: {status} | Expiry: {expiry_date}\n"
                f"  {time_info}"
            )
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error querying patent data: {str(e)}"


@tool("Check Patent Expiry")
def check_patent_expiry(molecule: str, country: str = "US") -> str:
    """
    Check when patents expire for a molecule to assess generic entry opportunity.
    
    Args:
        molecule: Name of the molecule to check.
        country: Country for patent check (default: US).
    
    Returns:
        Patent expiry date and whether generic entry is possible.
    """
    try:
        data = _load_patent_data()
        
        result = None
        for entry in data:
            if molecule.lower() in entry.get("molecule", "").lower():
                result = entry
                break
        
        if not result:
            return f"No patent data found for {molecule}"
        
        # Find earliest unexpired and latest expired patents
        today = datetime.now()
        active_patents = []
        expired_patents = []
        
        for patent in result.get("patents", []):
            expiry = datetime.strptime(patent["expiry_date"], "%Y-%m-%d")
            patent_info = {
                "number": patent["patent_number"],
                "type": patent["type"],
                "expiry": patent["expiry_date"],
                "days": (expiry - today).days
            }
            
            if patent["status"] == "Expired" or expiry < today:
                expired_patents.append(patent_info)
            else:
                active_patents.append(patent_info)
        
        output = [f"**Patent Expiry Analysis for {result['molecule']} ({country}):**\n"]
        
        if not active_patents:
            output.append("✅ **GENERIC ENTRY POSSIBLE** - All patents expired\n")
            output.append("Expired Patents:")
            for p in expired_patents:
                output.append(f"  - {p['number']} ({p['type']}): Expired {p['expiry']}")
        else:
            # Sort by expiry date
            active_patents.sort(key=lambda x: x["days"])
            earliest = active_patents[0]
            
            if earliest["days"] < 365:
                output.append(f"⚠️ **PATENT EXPIRING SOON** - {earliest['days']} days remaining\n")
            else:
                years = earliest["days"] // 365
                output.append(f"🔒 **PATENT PROTECTED** - ~{years} years remaining\n")
            
            output.append("Active Patents:")
            for p in active_patents:
                output.append(f"  - {p['number']} ({p['type']}): Expires {p['expiry']}")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error checking patent expiry: {str(e)}"


@tool("Assess FTO Risk")
def assess_fto_risk(molecule: str) -> str:
    """
    Assess Freedom to Operate (FTO) risk for a molecule.
    
    Args:
        molecule: Name of the molecule to assess.
    
    Returns:
        FTO risk level (High/Medium/Low) with explanation.
    """
    try:
        data = _load_patent_data()
        
        result = None
        for entry in data:
            if molecule.lower() in entry.get("molecule", "").lower():
                result = entry
                break
        
        if not result:
            return f"No patent data found for {molecule}. FTO risk: UNCLEAR"
        
        today = datetime.now()
        active_com_patents = 0  # Composition of Matter
        active_form_patents = 0  # Formulation
        
        for patent in result.get("patents", []):
            expiry = datetime.strptime(patent["expiry_date"], "%Y-%m-%d")
            if expiry > today:
                if "composition" in patent["type"].lower():
                    active_com_patents += 1
                else:
                    active_form_patents += 1
        
        # Determine risk level
        if active_com_patents > 0:
            risk_level = "HIGH"
            explanation = "Active Composition of Matter patent blocks generic development"
        elif active_form_patents > 0:
            risk_level = "MEDIUM"
            explanation = "Formulation patents exist but can potentially be designed around"
        else:
            risk_level = "LOW"
            explanation = "No active blocking patents - clear path for generic development"
        
        return (
            f"**FTO Risk Assessment for {result['molecule']}:**\n\n"
            f"Risk Level: **{risk_level}**\n"
            f"Explanation: {explanation}\n\n"
            f"Active Composition Patents: {active_com_patents}\n"
            f"Active Formulation Patents: {active_form_patents}"
        )
    
    except Exception as e:
        return f"Error assessing FTO risk: {str(e)}"
