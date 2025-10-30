"""Testing framework for Context Engineering pipelines.

Provides strategy pattern for composable testing with pluggable mock strategies.
Enables unit/integration/E2E testing patterns with observable mocking.
"""

__version__ = "0.1.0"

from .strategy import NodeStrategy, BaseRealStrategy, BaseMockStrategy
from .mocks import MockSerenaStrategy, MockContext7Strategy, MockLLMStrategy
from .builder import Pipeline, PipelineBuilder
from .real_strategies import RealParserStrategy, RealCommandStrategy

__all__ = [
    "NodeStrategy",
    "BaseRealStrategy",
    "BaseMockStrategy",
    "MockSerenaStrategy",
    "MockContext7Strategy",
    "MockLLMStrategy",
    "Pipeline",
    "PipelineBuilder",
    "RealParserStrategy",
    "RealCommandStrategy",
]
