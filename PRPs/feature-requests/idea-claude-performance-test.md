## Coleman00 Context Engineering Framework

### Core Principles

**Context Engineering** represents a paradigm shift from traditional prompt engineering—it's a **complete system** for providing comprehensive context to AI coding assistants through documentation, examples, rules, patterns, and validation.[1][2]

**Key differentiation:**
- **Prompt Engineering:** Focuses on clever wording/phrasing (like giving a sticky note)
- **Context Engineering:** Provides comprehensive context including documentation, examples, rules, patterns, validation (like writing a full screenplay with all details)[1]

### Architecture: Four Pillars

The framework organizes context management into **four fundamental operations**:[3]

**1. Write (Persisting State)**
- Stores information generated during tasks for later use
- Creates institutional memory extending beyond single LLM calls
- Enables persistent knowledge building

**2. Select (Dynamic Retrieval)**
- Fetches relevant information from external sources at runtime
- Loads context window with right information at right time
- Powers RAG (Retrieval-Augmented Generation) patterns

**3. Compress**
- Optimizes token usage in context window
- Reduces redundancy while preserving information density

**4. Isolate**
- Separates concerns to prevent context contamination
- Manages task-specific boundaries

### Implementation Components

**Global Rules (CLAUDE.md)**:[1]
- Project awareness (planning docs, tasks)
- Code structure (file size limits, module organization)
- Testing requirements (unit test patterns, coverage expectations)
- Style conventions (language preferences, formatting)
- Documentation standards (docstring formats, commenting)

**Example Workflows**:
- Code structure patterns (modules, imports, class/function patterns)
- Testing patterns (test file structure, mocking, assertions)
- Integration patterns (API clients, database connections, auth flows)
- CLI patterns (argument parsing, output formatting, error handling)

---

## Testing Claude Model Performance: Comprehensive Framework

### Model Comparison Overview

**Claude Haiku 4.5** (Released Oct 15, 2025):[4][5]
- **Performance:** 73.3% on SWE-bench Verified (real-world bug fixing)
- **Speed:** Sub-200ms latency for small prompts, 2-3× faster than Sonnet
- **Cost:** $1 input / $5 output per 1M tokens
- **Context Window:** 200K tokens
- **Computer Use:** 50.7% success rate on OSWorld benchmark

**Claude Sonnet 4.5** (Released Sep 29, 2025):[6][5]
- **Performance:** ~87% on GSM8K (math/logic), ~80% on HumanEval (code generation)
- **Speed:** 500-800ms latency
- **Cost:** Higher per-token rate
- **Context Window:** 200K tokens
- **Use Case:** Complex reasoning, multi-step logic, critical decisions

**Important:** Claude Haiku 3.5 was deprecated/retired on October 28, 2025. Claude Haiku 4.5 is the current active model.[7][8][9]

### Performance Testing Programs

#### Program 1: Sonnet 4.5 Challenge (Complex Multi-Step Reasoning)

```python
"""
Distributed Task Scheduler with Conflict Resolution
- Multi-threaded job processing with dependency graphs
- Dynamic priority queue with weighted constraints
- Deadlock detection and resolution
- Resource allocation optimization
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import heapq
from threading import Lock
import time

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Job:
    """Represents a schedulable job with dependencies and resources."""
    id: str
    priority: int
    duration: float
    dependencies: List[str]
    required_resources: Set[str]
    max_retries: int = 3
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first

class DistributedScheduler:
    """
    Implement a distributed task scheduler that:
    1. Manages job dependencies (DAG validation)
    2. Detects and resolves deadlocks using Banker's algorithm
    3. Allocates resources with conflict resolution
    4. Implements priority-based scheduling with starvation prevention
    5. Handles concurrent job execution with thread-safety
    6. Provides real-time monitoring and statistics
    
    Requirements:
    - Detect circular dependencies before execution
    - Implement aging to prevent priority inversion
    - Track resource utilization and suggest optimization
    - Generate execution timeline visualization (Gantt chart data)
    - Handle edge cases: resource exhaustion, cascade failures
    """
    
    def __init__(self, available_resources: Set[str], max_concurrent: int):
        self.available_resources = available_resources
        self.max_concurrent = max_concurrent
        self.job_queue: List[Job] = []
        self.job_status: Dict[str, JobStatus] = {}
        self.resource_allocation: Dict[str, str] = {}  # resource -> job_id
        self.lock = Lock()
        
    def add_job(self, job: Job) -> bool:
        """Add job with dependency validation. Return True if valid."""
        pass
    
    def detect_deadlock(self) -> Optional[List[str]]:
        """Use cycle detection to find deadlocked job chains."""
        pass
    
    def resolve_conflict(self, job1_id: str, job2_id: str) -> str:
        """Determine which job gets priority in resource conflict."""
        pass
    
    def execute_schedule(self) -> Dict[str, any]:
        """Execute all jobs and return statistics."""
        pass
    
    def generate_gantt_data(self) -> List[Dict]:
        """Generate timeline data for visualization."""
        pass

# Test Cases
if __name__ == "__main__":
    scheduler = DistributedScheduler(
        available_resources={"CPU", "GPU", "Memory", "Network"},
        max_concurrent=4
    )
    
    # Create complex dependency graph
    jobs = [
        Job("A", priority=5, duration=2.0, dependencies=[], 
            required_resources={"CPU", "Memory"}),
        Job("B", priority=8, duration=1.5, dependencies=["A"], 
            required_resources={"GPU"}),
        Job("C", priority=3, duration=3.0, dependencies=["A"], 
            required_resources={"CPU", "Network"}),
        Job("D", priority=9, duration=1.0, dependencies=["B", "C"], 
            required_resources={"GPU", "Memory"}),
        # Add edge case: potential circular dependency
        Job("E", priority=6, duration=2.5, dependencies=["D"], 
            required_resources={"Network"}),
    ]
    
    for job in jobs:
        scheduler.add_job(job)
    
    stats = scheduler.execute_schedule()
    print(f"Execution Statistics: {stats}")
    gantt = scheduler.generate_gantt_data()
    print(f"Timeline: {gantt}")
```

**Evaluation Criteria:**
- Correct DAG validation and cycle detection
- Proper deadlock detection implementation
- Thread-safe resource management
- Priority queue with aging mechanism
- Complete statistics generation
- Edge case handling (resource exhaustion, failures)

#### Program 2: Haiku 4.5 Challenge (Fast Agent-Style Automation)

```python
"""
Intelligent Log Parser with Pattern Learning
- Real-time log stream processing
- Adaptive pattern recognition
- Anomaly detection with auto-correction suggestions
- Performance optimization with caching
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict, deque
import re

@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: datetime
    level: str  # DEBUG, INFO, WARN, ERROR, CRITICAL
    service: str
    message: str
    metadata: Dict[str, str]

class LogAnalyzer:
    """
    Implement an intelligent log analyzer that:
    1. Parses multiple log formats (JSON, syslog, custom)
    2. Learns common patterns and detects anomalies
    3. Correlates related error chains across services
    4. Suggests auto-fixes based on known resolutions
    5. Generates real-time alerts with severity scoring
    6. Optimizes performance for streaming logs (10K+ entries/sec)
    
    Requirements:
    - Auto-detect log format from sample lines
    - Build pattern dictionary from historical logs
    - Use sliding window for anomaly detection
    - Implement efficient string matching (Aho-Corasick or similar)
    - Cache parsed patterns with TTL
    - Handle malformed/truncated log entries gracefully
    """
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.pattern_cache: Dict[str, int] = defaultdict(int)
        self.recent_logs: deque = deque(maxlen=window_size)
        self.known_patterns: Dict[str, List[str]] = {}
        self.anomaly_threshold: float = 0.15
        
    def detect_format(self, sample_lines: List[str]) -> str:
        """Auto-detect log format from sample. Return format type."""
        pass
    
    def parse_entry(self, raw_line: str, format_type: str) -> Optional[LogEntry]:
        """Parse raw log line into structured entry."""
        pass
    
    def learn_pattern(self, entry: LogEntry) -> bool:
        """Update pattern dictionary. Return True if new pattern."""
        pass
    
    def detect_anomaly(self, entry: LogEntry) -> Tuple[bool, float]:
        """Check if entry is anomalous. Return (is_anomaly, confidence)."""
        pass
    
    def correlate_errors(self, service: str, time_window: int) -> List[List[LogEntry]]:
        """Find related error chains within time window (seconds)."""
        pass
    
    def suggest_fix(self, error_pattern: str) -> Optional[str]:
        """Suggest resolution based on known patterns."""
        pass
    
    def generate_alert(self, entry: LogEntry, anomaly_score: float) -> Dict:
        """Create structured alert with severity and context."""
        pass
    
    def get_statistics(self) -> Dict[str, any]:
        """Return performance and analysis statistics."""
        pass

# Test Cases
if __name__ == "__main__":
    analyzer = LogAnalyzer(window_size=1000)
    
    # Sample logs in different formats
    sample_logs = [
        '2025-11-16T15:30:45Z INFO [auth-service] User login successful user_id=12345',
        '{"timestamp":"2025-11-16T15:30:46Z","level":"ERROR","service":"payment","message":"Transaction failed","error_code":"INSUFFICIENT_FUNDS"}',
        'Nov 16 15:30:47 api-gateway[8472]: WARN Connection timeout after 30s endpoint=/api/users',
        '2025-11-16T15:30:48Z CRITICAL [database] Deadlock detected table=orders query_id=99821',
    ]
    
    # Detect format
    log_format = analyzer.detect_format(sample_logs)
    print(f"Detected format: {log_format}")
    
    # Process logs
    for raw_log in sample_logs:
        entry = analyzer.parse_entry(raw_log, log_format)
        if entry:
            is_new = analyzer.learn_pattern(entry)
            is_anomaly, score = analyzer.detect_anomaly(entry)
            
            if is_anomaly:
                alert = analyzer.generate_alert(entry, score)
                fix = analyzer.suggest_fix(entry.message)
                print(f"ANOMALY: {alert}")
                if fix:
                    print(f"Suggested fix: {fix}")
    
    # Correlate errors
    error_chains = analyzer.correlate_errors("payment", time_window=300)
    print(f"Found {len(error_chains)} error chains")
    
    # Statistics
    stats = analyzer.get_statistics()
    print(f"Analysis stats: {stats}")
```

**Evaluation Criteria:**
- Accurate multi-format log parsing
- Efficient pattern matching and caching
- Correct anomaly detection (sliding window)
- Meaningful error correlation
- Practical auto-fix suggestions
- Performance optimization (throughput metrics)

### Automated Evaluation Pipeline

```python
"""
Claude Model Performance Evaluator
Executes test programs and analyzes results programmatically
"""

import anthropic
import time
from typing import Dict, List
import json

class ClaudePerformanceEvaluator:
    """
    Automated evaluation framework for Claude model testing.
    """
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def run_test(self, 
                 model: str, 
                 test_program: str,
                 test_name: str) -> Dict:
        """Execute test program and collect metrics."""
        
        start_time = time.time()
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=8000,
                temperature=0.0,  # Deterministic for testing
                messages=[{
                    "role": "user",
                    "content": f"""Complete the following program implementation:

{test_program}

Implement ALL methods with complete, production-ready code.
Include error handling, type hints, and docstrings.
Ensure thread-safety where applicable."""
                }]
            )
            
            end_time = time.time()
            
            # Extract response
            code_response = response.content[0].text
            
            # Collect metrics
            metrics = {
                "model": model,
                "test_name": test_name,
                "latency_seconds": end_time - start_time,
                "response_length": len(code_response),
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "code_output": code_response,
                "success": True
            }
            
            return metrics
            
        except Exception as e:
            return {
                "model": model,
                "test_name": test_name,
                "success": False,
                "error": str(e)
            }
    
    def evaluate_code_quality(self, code: str) -> Dict[str, float]:
        """Use LLM-as-judge to evaluate code quality."""
        
        evaluation_prompt = f"""Evaluate the following code implementation on these criteria (0-10 scale):

1. **Correctness**: Does it implement all required methods? Are algorithms correct?
2. **Completeness**: Are all edge cases handled? All features implemented?
3. **Code Quality**: Clean, readable, well-structured? Good naming?
4. **Error Handling**: Robust error handling and validation?
5. **Performance**: Efficient algorithms and data structures?
6. **Thread Safety**: Proper locking and concurrency handling?

Code to evaluate:
```
{code}
```

Respond with JSON only:
{{
    "correctness": <score>,
    "completeness": <score>,
    "code_quality": <score>,
    "error_handling": <score>,
    "performance": <score>,
    "thread_safety": <score>,
    "reasoning": "<brief explanation>"
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4.5",  # Use Sonnet as judge
            max_tokens=2000,
            temperature=0.0,
            messages=[{"role": "user", "content": evaluation_prompt}]
        )
        
        # Parse JSON response
        try:
            eval_result = json.loads(response.content[0].text)
            return eval_result
        except:
            return {"error": "Failed to parse evaluation"}
    
    def run_full_evaluation(self) -> Dict:
        """Run complete evaluation suite."""
        
        # Test configurations
        tests = [
            {
                "model": "claude-sonnet-4.5",
                "test_program": SONNET_TEST_PROGRAM,  # From above
                "test_name": "Distributed Scheduler (Sonnet)"
            },
            {
                "model": "claude-haiku-4.5",
                "test_program": HAIKU_TEST_PROGRAM,  # From above
                "test_name": "Log Analyzer (Haiku)"
            }
        ]
        
        results = []
        
        for test_config in tests:
            print(f"\nRunning: {test_config['test_name']}")
            
            # Execute test
            metrics = self.run_test(
                model=test_config['model'],
                test_program=test_config['test_program'],
                test_name=test_config['test_name']
            )
            
            if metrics['success']:
                # Evaluate code quality
                quality_scores = self.evaluate_code_quality(
                    metrics['code_output']
                )
                metrics['quality_evaluation'] = quality_scores
                
                # Calculate cost
                input_cost = metrics['input_tokens'] / 1_000_000
                output_cost = metrics['output_tokens'] / 1_000_000
                
                if 'sonnet' in test_config['model']:
                    # Sonnet pricing (example rates)
                    cost = input_cost * 3 + output_cost * 15
                else:  # Haiku
                    cost = input_cost * 1 + output_cost * 5
                    
                metrics['estimated_cost_usd'] = cost
            
            results.append(metrics)
        
        return {
            "timestamp": time.time(),
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate comparative summary."""
        
        summary = {
            "total_tests": len(results),
            "successful_tests": sum(1 for r in results if r['success']),
            "models_compared": list(set(r['model'] for r in results))
        }
        
        # Compare latencies
        latencies = {r['model']: r['latency_seconds'] 
                    for r in results if r['success']}
        summary['latency_comparison'] = latencies
        
        # Compare quality scores
        quality_avg = {}
        for result in results:
            if 'quality_evaluation' in result:
                model = result['model']
                scores = result['quality_evaluation']
                avg_score = sum(scores.values()) / len(scores) if scores else 0
                quality_avg[model] = avg_score
        
        summary['quality_comparison'] = quality_avg
        
        return summary

# Usage
if __name__ == "__main__":
    evaluator = ClaudePerformanceEvaluator(api_key="your-api-key")
    results = evaluator.run_full_evaluation()
    
    print(json.dumps(results, indent=2))
```

### Evaluation Frameworks Integration

**Recommended Tools**:[10][11]

**DeepEval**:[10]
- 14+ LLM evaluation metrics (G-Eval, Hallucination, Faithfulness, etc.)
- Supports both RAG and fine-tuning use cases
- Python-native evaluation pipeline

**LangSmith**:[11]
- Rapid prototyping with LangChain/LangGraph integration
- Fast regression testing during dev cycles
- Adaptive LLM evaluators that learn from corrections
- Visualization tools for experiment tracking

**MLFlow LLM Evaluate**:[10]
- Intuitive developer experience
- Simple evaluation pipeline setup
- Good for QA and RAG evaluation

### Evaluation Metrics

**Automated Metrics**:[12][13]
- **Perplexity:** Measures predictive capability (lower = better)
- **BLEU:** Evaluates text quality via n-gram precision
- **Latency:** Response time under real workloads
- **Token Efficiency:** Cost per task completion
- **Correctness:** Passes test cases and meets requirements

**Application-Centric Metrics**:[13]
- **Hallucination Rate:** Factual accuracy verification
- **Context Relevance:** Maintains focus on task
- **Task Completion:** Successfully implements all requirements
- **Code Quality:** Readability, structure, best practices
- **Resource Usage:** Memory, CPU, API costs

### Testing Methodology

**Pointwise Testing**:[13]
- Evaluate each response individually
- Assign quality scores/ratings
- Best for queries with definitive correct answers

**Pairwise Testing**:[13]
- Compare two model responses side-by-side
- Determine which is more accurate/clear
- Best for open-ended tasks without single correct answer

**Implementation Steps:**

1. **Prepare Test Programs** (see above for Sonnet/Haiku challenges)
2. **Execute Tests** via API with controlled parameters (temperature=0)
3. **Collect Metrics** (latency, tokens, cost)
4. **Automated Evaluation** using LLM-as-judge (Sonnet 4.5)
5. **Statistical Analysis** across 50+ runs for reliability[4]
6. **Generate Report** with comparative performance data

Citations:
[1] [coleam00/context-engineering-intro - GitHub](https://github.com/coleam00/context-engineering-intro)  
[2] [Beyond Prompts: How Context Engineering Is Shaping the Next ...](https://insights.firstaimovers.com/beyond-prompts-how-context-engineering-is-shaping-the-next-wave-of-ai-c13f5e6dffc8)  
[3] [From Vibe Coding to Context Engineering - Sundeep Teki](https://www.sundeepteki.org/blog/from-vibe-coding-to-context-engineering-a-blueprint-for-production-grade-genai-systems)  
[4] [Claude Haiku 4.5: Features, Testing Results, and Use Cases](https://www.datacamp.com/fr/blog/anthropic-claude-haiku-4-5)  
[5] [Claude (language model) - Wikipedia](https://en.wikipedia.org/wiki/Claude_(language_model))  
[6] [Claude Haiku 4.5 vs Sonnet 4.5: Detailed Comparison 2025](https://www.creolestudios.com/claude-haiku-4-5-vs-sonnet-4-5-comparison/)  
[7] [Claude Sonnet 3.5 deprecated, Claude Haiku 4.5 available in ...](https://github.blog/changelog/2025-11-10-claude-sonnet-3-5-deprecated-claude-haiku-4-5-available-in-copilot-free/)  
[8] [Model deprecations - Claude Docs](https://docs.claude.com/en/docs/about-claude/model-deprecations)  
[9] [Claude Developer Platform](https://docs.claude.com/en/release-notes/overview)  
[10] [‼️ Top 5 Open-Source LLM Evaluation Frameworks in 2025 - DEV ...](https://dev.to/guybuildingai/-top-5-open-source-llm-evaluation-frameworks-in-2024-98m)  
[11] [Comparing LLM Evaluation Platforms: Top Frameworks for 2025](https://arize.com/llm-evaluation-platforms-top-frameworks/)  
[12] [LLM Evaluation: Metrics, Methodologies, Best Practices](https://www.datacamp.com/blog/llm-evaluation)  
[13] [LLM Testing: The Latest Techniques & Best Practices](https://www.patronus.ai/llm-testing)  
[14] [Context Engineering Template for AI Agents. 100 ... - Facebook](https://www.facebook.com/0xSojalSec/posts/context-engineering-template-for-ai-agents100-opensource-httpsgithubcomcoleam00c/1338385644482502/)  
[15] [Context Engineering is the New Vibe Coding (Learn this Now)](https://www.youtube.com/watch?v=Egeuql3Lrzg)  
[16] [Agentic Context Engineering (ACE): The Future of AI is Here](https://enoumen.substack.com/p/agentic-context-engineering-ace-the)  
[17] [Claude Haiku 4.5 vs Sonnet 4.5 vs GPT-5 – Which one is ...](https://blog.getbind.co/2025/10/16/claude-haiku-4-5-vs-sonnet-4-5-vs-gpt-5-which-one-is-better/)  
[18] [Deprecating on 11/30/2025 - Retell AI](https://docs.retellai.com/deprecation-notice/11-30)  
[19] [All Claude AI models available in 2025: full list for web, app, API ...](https://www.datastudios.org/post/all-claude-ai-models-available-in-2025-full-list-for-web-app-api-and-cloud-platforms)  
[20] [Mini Models Battle: Claude Haiku 4.5 vs GLM-4.6 vs GPT-5 Mini](https://blog.kilocode.ai/p/mini-models-battle-claude-haiku-45)