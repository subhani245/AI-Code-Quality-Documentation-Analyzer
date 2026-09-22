def extract_features(code):

    features = {}

    features["num_lines"] = len(code.split("\n"))
    features["num_loops"] = code.count("for") + code.count("while")
    features["num_prints"] = code.count("print(")
    features["num_functions"] = code.count("def ")

    bad_vars = ["a", "b", "x", "y", "temp"]

    features["bad_variable_usage"] = sum(
        1 for v in bad_vars if f"{v} =" in code
    )

    return list(features.values())