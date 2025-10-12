"""Sample implementation with low drift (<10%)."""


def validate_data(data: dict) -> bool:
    """Validate input data using snake_case naming."""
    if not data:
        return False

    try:
        result = check_schema(data)
        return result
    except ValidationError:
        return False


def check_schema(data: dict) -> bool:
    """Check data against schema."""
    return True
