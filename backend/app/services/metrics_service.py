"""
Metrics Collection Service
Tracks RAG performance metrics for monitoring and optimization
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    timestamp: str
    query: str
    query_length: int
    tier_used: str  # "tier1", "tier2", or "no_context"
    documents_retrieved: int
    avg_similarity_score: float
    max_similarity_score: float
    category: Optional[str]
    confidence: float
    response_generated: bool
    error: Optional[str] = None


class MetricsCollector:
    """Collects and aggregates RAG performance metrics"""

    def __init__(self, metrics_file: Optional[str] = None):
        """
        Initialize metrics collector.

        Args:
            metrics_file: Path to JSON file for storing metrics (optional)
        """
        self.metrics_file = Path(metrics_file) if metrics_file else None
        self.query_metrics: List[QueryMetrics] = []

        # Aggregated metrics
        self.total_queries = 0
        self.queries_with_context = 0
        self.tier1_success = 0
        self.tier2_success = 0
        self.no_context = 0

        self.category_counts = defaultdict(int)
        self.tier1_scores: List[float] = []
        self.tier2_scores: List[float] = []
        self.failed_queries: List[Dict] = []

        logger.info("Metrics Collector initialized")

    def log_query(
        self,
        query: str,
        tier: str,
        documents: List[Dict],
        category: Optional[str],
        confidence: float,
        error: Optional[str] = None
    ):
        """
        Log metrics for a single query.

        Args:
            query: User query
            tier: Tier used ("tier1", "tier2", "no_context")
            documents: Retrieved documents
            category: Detected category
            confidence: Response confidence score
            error: Error message if any
        """
        self.total_queries += 1

        # Calculate metrics
        num_docs = len(documents)
        if num_docs > 0:
            self.queries_with_context += 1
            scores = [doc.get("score", 0.0) for doc in documents]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
        else:
            avg_score = 0.0
            max_score = 0.0

        # Update tier counters
        if tier == "tier1":
            self.tier1_success += 1
            self.tier1_scores.append(avg_score)
        elif tier == "tier2":
            self.tier2_success += 1
            self.tier2_scores.append(avg_score)
        else:  # no_context
            self.no_context += 1
            self.failed_queries.append({
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "error": error
            })

        # Update category counts
        if category:
            self.category_counts[category] += 1

        # Create query metric
        metric = QueryMetrics(
            timestamp=datetime.utcnow().isoformat(),
            query=query[:200],  # Truncate long queries
            query_length=len(query),
            tier_used=tier,
            documents_retrieved=num_docs,
            avg_similarity_score=round(avg_score, 3),
            max_similarity_score=round(max_score, 3),
            category=category,
            confidence=round(confidence, 3),
            response_generated=num_docs > 0,
            error=error
        )

        self.query_metrics.append(metric)

        # Persist to file if configured
        if self.metrics_file:
            self._append_to_file(metric)

        logger.debug(
            f"Logged query metric: tier={tier}, docs={num_docs}, "
            f"avg_score={avg_score:.3f}, confidence={confidence:.3f}"
        )

    def get_summary(self) -> Dict:
        """
        Get summary of all collected metrics.

        Returns:
            Dictionary with aggregated metrics
        """
        response_rate = (
            self.queries_with_context / max(self.total_queries, 1)
        )
        tier1_rate = self.tier1_success / max(self.total_queries, 1)
        tier2_rate = self.tier2_success / max(self.total_queries, 1)
        no_context_rate = self.no_context / max(self.total_queries, 1)

        avg_tier1_score = (
            sum(self.tier1_scores) / len(self.tier1_scores)
            if self.tier1_scores else 0.0
        )
        avg_tier2_score = (
            sum(self.tier2_scores) / len(self.tier2_scores)
            if self.tier2_scores else 0.0
        )

        return {
            "total_queries": self.total_queries,
            "response_rate": round(response_rate, 3),
            "tier_distribution": {
                "tier1_success": self.tier1_success,
                "tier1_rate": round(tier1_rate, 3),
                "tier2_success": self.tier2_success,
                "tier2_rate": round(tier2_rate, 3),
                "no_context": self.no_context,
                "no_context_rate": round(no_context_rate, 3),
            },
            "similarity_scores": {
                "tier1_avg": round(avg_tier1_score, 3),
                "tier2_avg": round(avg_tier2_score, 3),
            },
            "category_distribution": dict(self.category_counts),
            "failed_queries_count": len(self.failed_queries),
            "recent_failures": self.failed_queries[-10:],  # Last 10 failures
        }

    def get_detailed_metrics(self) -> List[Dict]:
        """
        Get detailed metrics for all queries.

        Returns:
            List of query metric dictionaries
        """
        return [asdict(metric) for metric in self.query_metrics]

    def reset_metrics(self):
        """Reset all collected metrics"""
        self.query_metrics.clear()
        self.total_queries = 0
        self.queries_with_context = 0
        self.tier1_success = 0
        self.tier2_success = 0
        self.no_context = 0
        self.category_counts.clear()
        self.tier1_scores.clear()
        self.tier2_scores.clear()
        self.failed_queries.clear()
        logger.info("Metrics reset")

    def _append_to_file(self, metric: QueryMetrics):
        """
        Append metric to JSON file.

        Args:
            metric: Query metric to append
        """
        try:
            # Ensure parent directory exists
            if self.metrics_file:
                self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

                # Append as newline-delimited JSON
                with open(self.metrics_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(asdict(metric)) + '\n')
        except Exception as e:
            logger.error(f"Failed to write metric to file: {e}")


# Singleton instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(metrics_file: Optional[str] = None) -> MetricsCollector:
    """
    Get or create the metrics collector singleton.

    Args:
        metrics_file: Path to metrics file (only used on first call)

    Returns:
        MetricsCollector instance
    """
    global _metrics_collector
    if _metrics_collector is None:
        # Default metrics file in backend/logs
        default_file = Path(__file__).parent.parent.parent / "logs" / "query_metrics.jsonl"
        _metrics_collector = MetricsCollector(
            metrics_file=metrics_file or str(default_file)
        )
    return _metrics_collector
