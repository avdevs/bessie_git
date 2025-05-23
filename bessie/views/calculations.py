def calculate_stress_load(factors):
    """
    Calculate stress load percentage based on given factors.

    Args:
        factors (list): A list of dictionaries, each containing a 'val' key with counts.

    Returns:
        float: Stress load percentage.
    """
    if not factors or not isinstance(factors, list):  # Ensure valid data
        return 0

    medium = high = very_high = total = 0

    for factor in factors:
        if isinstance(factor, dict) and "val" in factor:
            val = factor["val"]  # Extract 'val' dictionary

            # Convert values to integers safely
            medium += int(val.get("medium_count", 0) or 0)
            high += int(val.get("high_count", 0) or 0)
            very_high += int(val.get("very_high", 0) or 0)

            total += sum(
                int(value)
                for value in val.values()
                if isinstance(value, int) or str(value).isdigit()
            )

    if total == 0:  # Avoid division by zero
        return 0

    stress_load = ((medium + high + very_high) / total) * 100
    return round(stress_load, 2)  # Return rounded percentage
