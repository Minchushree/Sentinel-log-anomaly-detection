import pandas as pd

def extract_features(parsed_log):
    return pd.DataFrame([{
        "status": parsed_log["status"],
        "length": parsed_log["length"]
    }])
