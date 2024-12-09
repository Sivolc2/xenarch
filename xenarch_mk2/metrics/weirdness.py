from typing import Any, Dict, List
import numpy as np

class WeirdnessMetrics:
    """Compute various metrics for quantifying anomalous features"""
    
    @staticmethod
    def compute_local_deviation(region: np.ndarray) -> float:
        """Compute how much a region deviates from its surroundings"""
        raise NotImplementedError
    
    @staticmethod
    def rank_anomalies(regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank regions by their anomaly scores"""
        raise NotImplementedError 