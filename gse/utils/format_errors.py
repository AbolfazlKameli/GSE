def format_errors(errors):
    formatted_errors = {}
    for field, error in errors.items():
        if isinstance(error, list):
            formatted_errors[field] = error[0]
        elif isinstance(error, dict):
            formatted_errors[field] = {key: val[0] if isinstance(val, list) else val for key, val in
                                       error.items()}
        else:
            formatted_errors[field] = error
    return formatted_errors
