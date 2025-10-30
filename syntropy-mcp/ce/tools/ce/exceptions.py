"""Custom exceptions for PRP execution orchestration."""


class EscalationRequired(Exception):
    """Raised when automatic self-healing fails and human intervention is needed.

    Attributes:
        reason: Escalation trigger reason (persistent_error, ambiguous, architecture, dependencies, security)
        error: Parsed error dict that triggered escalation
        troubleshooting: Multi-line troubleshooting guidance for user
    """

    def __init__(
        self,
        reason: str,
        error: dict,
        troubleshooting: str
    ):
        self.reason = reason
        self.error = error
        self.troubleshooting = troubleshooting

        # Format error message
        error_type = error.get("type", "unknown")
        error_msg = error.get("message", "No message")
        error_loc = f"{error.get('file', 'unknown')}:{error.get('line', '?')}"

        message = (
            f"Escalation required ({reason})\n"
            f"Error type: {error_type}\n"
            f"Location: {error_loc}\n"
            f"Message: {error_msg}\n\n"
            f"🔧 Troubleshooting:\n{troubleshooting}"
        )

        super().__init__(message)


class BlueprintParseError(ValueError):
    """Raised when PRP blueprint parsing fails."""

    def __init__(self, prp_path: str, issue: str):
        message = (
            f"Failed to parse PRP blueprint: {prp_path}\n"
            f"Issue: {issue}\n"
            f"🔧 Troubleshooting: Ensure PRP has well-formed IMPLEMENTATION BLUEPRINT section"
        )
        super().__init__(message)


class ValidationError(RuntimeError):
    """Raised when validation fails after max attempts."""

    def __init__(self, level: str, error_details: dict):
        self.level = level
        self.error_details = error_details

        message = (
            f"Validation failed at Level {level}\n"
            f"Attempts: {error_details.get('attempts', 0)}\n"
            f"Last error: {error_details.get('last_error', 'Unknown')}\n"
            f"🔧 Troubleshooting: Review validation output for specific errors"
        )
        super().__init__(message)


class ContextDriftError(RuntimeError):
    """Raised when context drift exceeds acceptable threshold.

    Attributes:
        drift_score: Drift percentage (0-100)
        threshold: Threshold that was exceeded
        troubleshooting: Multi-line troubleshooting guidance
    """

    def __init__(self, drift_score: float, threshold: float, troubleshooting: str):
        self.drift_score = drift_score
        self.threshold = threshold
        self.troubleshooting = troubleshooting

        message = (
            f"Context drift too high: {drift_score:.1f}% (threshold: {threshold:.1f}%)\n"
            f"🔧 Troubleshooting:\n{troubleshooting}"
        )
        super().__init__(message)
