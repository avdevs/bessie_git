def calculate_stress_load(factors):
  if not factors or not isinstance(factors, list):
    return 0

  medium = high = very_high = total = 0

  for factor in factors:
    if isinstance(factor, dict) and "val" in factor:
      val = factor["val"]

      medium += int(val.get("medium_count", 0) or 0)
      high += int(val.get("high_count", 0) or 0)
      very_high += int(val.get("very_high", 0) or 0)

      total += sum(
        int(value)
        for value in val.values()
        if isinstance(value, int) or str(value).isdigit()
      )

  if total == 0:
    return 0

  stress_load = ((medium + high + very_high) / total) * 100
  return round(stress_load, 2)
