\"\"\"
Schools database and normalization system.
Contains mappings for D1, D2, D3 baseball and D1 softball.
\"\"\"
import logging

logger = logging.getLogger(__name__)

# Comprehensive mapping of schools across divisions
# Format: \"Display Name\": { \"ncaa_name\": \"...\", \"platform\": \"...\", \"division\": \"...\", \"sport\": \"...\" }
SCHOOLS_DB = {
    # D1 Baseball - ACC
    \"Georgia Tech\": {
        \"ncaa_name\": \"Georgia Institute of Technology\",
        \"platform\": \"sidearm\",
        \"division\": \"D1\",
        \"sport\": \"baseball\",
        "team_website": "https://ramblinwreck.com/sports/baseball/schedule"
    },
    \"North Carolina\": {
        \"ncaa_name\": \"University of North Carolina\",
        \"platform\": \"sidearm\",
        \"division\": \"D1\",
        \"sport\": \"baseball\",
        "team_website": "https://goheels.com/sports/baseball/schedule"
    },
    # Add more D1 schools here...

    # D1 Softball
    \"Oklahoma\": {
        \"ncaa_name\": \"University of Oklahoma\",
        \"platform\": \"sidearm\",
        \"division\": \"D1\",
        \"sport\": \"softball\",
        "team_website": "https://soonersports.com/sports/softball/schedule"
    },
    # Add more softball schools here...

    # D2/D3 Baseball examples
    \"Belmont Abbey\": {
        \"ncaa_name\": \"Belmont Abbey College\",
        \"platform\": \"presto\",
        \"division\": \"D2\",
        \"sport\": \"baseball\",
        "team_website": "https://abbeyathletics.com/sports/baseball/schedule"
    }
}

def get_school_config(school_name, sport=\"baseball\"):
    \"\"\"Get configuration for a school\"\"\"
    # Case-insensitive lookup
    for name, config in SCHOOLS_DB.items():
        if name.lower() == school_name.lower() and config[\"sport\"] == sport:
            return config
    
    # Fallback if not found
    logger.warning(f\"School '{school_name}' for {sport} not found in database\")
    return None
