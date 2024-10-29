def format_errors(errors):
    return {field: error[0] for field, error in errors.items()}
