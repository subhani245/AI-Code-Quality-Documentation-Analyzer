def estimate_complexity(code):

    lines = code.split("\n")

    loop_count = 0
    nested_level = 0
    max_nested = 0

    for line in lines:

        if "for " in line or "while " in line:
            loop_count += 1
            nested_level += 1

            if nested_level > max_nested:
                max_nested = nested_level

        if line.strip() == "":
            nested_level = 0

    if max_nested == 0:
        return "O(1)"

    if max_nested == 1:
        return "O(n)"

    if max_nested == 2:
        return "O(n²)"

    if max_nested >= 3:
        return "O(n³) or higher"

    return "Unknown"