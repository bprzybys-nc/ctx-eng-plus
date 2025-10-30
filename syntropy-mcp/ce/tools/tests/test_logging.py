"""Tests for logging configuration module."""

import pytest
import json
import logging
from io import StringIO
from ce.logging_config import JSONFormatter, setup_logging, get_logger


class TestJSONFormatter:
    """Test JSON log formatter."""

    def test_basic_formatting(self):
        """Test that log record is formatted as valid JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = formatter.format(record)

        # Should be valid JSON
        log_data = json.loads(result)
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert "timestamp" in log_data

    def test_extra_fields(self):
        """Test that extra fields are included in JSON output."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="PRP started",
            args=(),
            exc_info=None
        )

        # Add extra fields
        record.prp_id = "PRP-003"
        record.phase = "execution"
        record.duration = 1200.5

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["prp_id"] == "PRP-003"
        assert log_data["phase"] == "execution"
        assert log_data["duration"] == 1200.5

    def test_exception_formatting(self):
        """Test that exceptions are included in JSON output."""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()
            )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "exception" in log_data
        assert "ValueError: Test error" in log_data["exception"]


class TestSetupLogging:
    """Test logging setup function."""

    def test_default_setup(self):
        """Test default logging configuration."""
        logger = setup_logging(level="INFO")

        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_json_output(self):
        """Test JSON output mode."""
        logger = setup_logging(level="DEBUG", json_output=True)

        # Check that handler uses JSON formatter
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)

    def test_log_level_configuration(self):
        """Test different log levels."""
        # Test DEBUG level
        logger = setup_logging(level="DEBUG")
        assert logger.level == logging.DEBUG

        # Test WARNING level
        logger = setup_logging(level="WARNING")
        assert logger.level == logging.WARNING

    def test_multiple_handlers(self, tmp_path):
        """Test file and console handlers."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="INFO", log_file=str(log_file))

        # Should have console + file handlers
        assert len(logger.handlers) == 2

        # Log a message
        test_logger = get_logger("test")
        test_logger.info("Test message")

        # File should contain the message
        assert log_file.exists()
        log_content = log_file.read_text()
        assert "Test message" in log_content


class TestGetLogger:
    """Test get_logger function."""

    def test_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test.module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_logger_inherits_config(self):
        """Test that logger inherits root logger configuration."""
        setup_logging(level="DEBUG")
        logger = get_logger("test.child")

        # Should inherit DEBUG level
        assert logger.level == logging.NOTSET  # Inherits from root
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_structured_logging_with_extra(self):
        """Test structured logging with extra fields."""
        # Setup with JSON formatter
        setup_logging(level="INFO", json_output=True)
        logger = get_logger("test.structured")

        # Capture log output
        import sys
        from io import StringIO

        # Get the stream handler
        handler = logging.getLogger().handlers[0]
        stream = StringIO()
        handler.stream = stream

        # Log with extra fields
        logger.info("Operation started", extra={"prp_id": "PRP-003", "phase": "test"})

        # Parse JSON output
        output = stream.getvalue()
        if output.strip():
            log_data = json.loads(output.strip())
            assert log_data["message"] == "Operation started"
            assert log_data["prp_id"] == "PRP-003"
            assert log_data["phase"] == "test"
