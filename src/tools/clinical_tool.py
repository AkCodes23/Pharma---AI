"""
Clinical Trials Tool
Queries mock clinical trials data for pipeline analysis.
"""
import json
from typing import Optional
from crewai.tools import tool
from pathlib import Path


def _load_clinical_data() -> list:
    """Load clinical trials mock data from JSON file."""
    data_path = Path(__file__).resolve().parent.parent.parent / "mock_data" / "clinical_trials.json"
    with open(data_path, "r") as f:
        return json.load(f)


@tool("Query Clinical Trials")
def query_clinical_trials(indication: Optional[str] = None, molecule: Optional[str] = None, therapy_area: Optional[str] = None) -> str:
    """
    Query active clinical trials by indication, molecule, or therapy area.
    
    Args:
        indication: Disease/condition to search (e.g., 'COPD', 'NSCLC', 'Diabetes')
        molecule: Drug name to search for in trials
        therapy_area: Therapeutic area (e.g., 'Respiratory', 'Oncology')
    
    Returns:
        List of active clinical trials with phase, sponsor, and competition density.
    """
    try:
        data = _load_clinical_data()
        results = []
        
        for entry in data:
            # Filter by indication
            if indication and indication.lower() not in entry.get("indication", "").lower():
                continue
            # Filter by therapy area
            if therapy_area and therapy_area.lower() not in entry.get("therapy_area", "").lower():
                continue
            # Filter by molecule (check in trials)
            if molecule:
                molecule_found = False
                for trial in entry.get("active_trials", []):
                    if molecule.lower() in trial.get("drug_name", "").lower():
                        molecule_found = True
                        break
                if not molecule_found:
                    continue
            
            results.append(entry)
        
        if not results:
            return f"No clinical trials found for indication='{indication}', molecule='{molecule}', therapy_area='{therapy_area}'"
        
        output = []
        for r in results:
            trials = r.get("active_trials", [])
            competition = r.get("competition_density", "Unknown")
            unmet_need = r.get("unmet_need", "Unknown")
            burden = r.get("patient_burden_score", "N/A")
            
            trial_info = f"**{r['indication']}** ({r.get('therapy_area', 'N/A')})\n"
            trial_info += f"  Competition Density: {competition} | Unmet Need: {unmet_need} | Patient Burden: {burden}\n"
            trial_info += f"  Active Trials: {len(trials)}\n"
            
            for trial in trials:
                trial_info += f"    - [{trial['phase']}] {trial['drug_name']} (Sponsor: {trial['sponsor']}) - {trial['nct_id']}\n"
            
            output.append(trial_info)
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error querying clinical trials: {str(e)}"


@tool("Find Repurposing Opportunities")
def find_repurposing_opportunities(molecule: str) -> str:
    """
    Find potential repurposing opportunities for a molecule by identifying new indications in trials.
    
    Args:
        molecule: Name of the molecule to find repurposing opportunities for.
    
    Returns:
        List of new indications where the molecule is being tested.
    """
    try:
        data = _load_clinical_data()
        opportunities = []
        
        for entry in data:
            for trial in entry.get("active_trials", []):
                if molecule.lower() in trial.get("drug_name", "").lower():
                    opportunities.append({
                        "indication": entry["indication"],
                        "therapy_area": entry.get("therapy_area", "N/A"),
                        "phase": trial["phase"],
                        "sponsor": trial["sponsor"],
                        "nct_id": trial["nct_id"],
                        "competition": entry.get("competition_density", "Unknown"),
                        "unmet_need": entry.get("unmet_need", "Unknown")
                    })
        
        if not opportunities:
            return f"No repurposing opportunities found for {molecule} in clinical trials."
        
        output = [f"**Repurposing Opportunities for {molecule}:**\n"]
        
        # Sort by phase (later phases = more advanced)
        phase_order = {"Phase IV": 0, "Phase III": 1, "Phase II": 2, "Phase I": 3}
        opportunities.sort(key=lambda x: phase_order.get(x["phase"], 4))
        
        for opp in opportunities:
            potential = "HIGH" if opp["phase"] in ["Phase III", "Phase IV"] and opp["competition"] == "Low" else "MEDIUM"
            
            output.append(
                f"- **{opp['indication']}** ({opp['therapy_area']})\n"
                f"  Phase: {opp['phase']} | Sponsor: {opp['sponsor']}\n"
                f"  Competition: {opp['competition']} | Unmet Need: {opp['unmet_need']}\n"
                f"  **Repurposing Potential: {potential}**\n"
            )
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error finding repurposing opportunities: {str(e)}"


@tool("Analyze Competition Density")
def analyze_competition_density(indication: str) -> str:
    """
    Analyze the competition density for a specific indication.
    
    Args:
        indication: Disease indication to analyze (e.g., 'COPD', 'Asthma', 'NSCLC')
    
    Returns:
        Competition analysis with trial counts and recommendations.
    """
    try:
        data = _load_clinical_data()
        
        result = None
        for entry in data:
            if indication.lower() in entry.get("indication", "").lower():
                result = entry
                break
        
        if not result:
            return f"No data found for indication: {indication}"
        
        trials = result.get("active_trials", [])
        competition = result.get("competition_density", "Unknown")
        unmet_need = result.get("unmet_need", "Unknown")
        burden = result.get("patient_burden_score", "N/A")
        
        # Count trials by phase
        phase_counts = {}
        sponsors = set()
        for trial in trials:
            phase = trial["phase"]
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            sponsors.add(trial["sponsor"])
        
        output = (
            f"**Competition Analysis for {result['indication']}:**\n\n"
            f"**Overall Competition:** {competition}\n"
            f"**Unmet Need:** {unmet_need}\n"
            f"**Patient Burden Score:** {burden}/10\n\n"
            f"**Trial Landscape:**\n"
            f"  - Total Active Trials: {len(trials)}\n"
            f"  - Unique Sponsors: {len(sponsors)}\n"
        )
        
        for phase, count in sorted(phase_counts.items()):
            output += f"  - {phase}: {count} trial(s)\n"
        
        # Recommendation
        output += "\n**Strategic Recommendation:**\n"
        if competition == "Low" and unmet_need in ["High", "Very High"]:
            output += "  ✅ **HIGH OPPORTUNITY** - Low competition with significant unmet need\n"
        elif competition == "Low":
            output += "  ✅ Favorable competitive landscape for entry\n"
        elif competition == "High":
            output += "  ⚠️ Crowded space - differentiation required\n"
        else:
            output += "  ℹ️ Moderate competition - targeted strategy needed\n"
        
        return output
    
    except Exception as e:
        return f"Error analyzing competition: {str(e)}"
