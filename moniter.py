import logging
from dataclasses import dataclass
from typing import List, Dict, Any
import time
import uuid

class ComplianceViolationType:
    POSITION_LIMIT = "Position Limit Exceeded"
    TRADING_HOURS = "Outside Trading Hours"
    MARKET_MANIPULATION = "Potential Market Manipulation"

@dataclass
class ComplianceEvent:
    """
    Record of compliance-related events and potential violations
    """
    event_id: str
    timestamp: float
    instrument: str
    violation_type: str
    details: Dict[str, Any]

class AuditLogger:
    """
    Immutable audit logging system for all trading actions
    """
    def __init__(self, log_file: str = 'trading_audit.log'):
        logging.basicConfig(
            filename=log_file, 
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        self.events: List[ComplianceEvent] = []
    
    def log_trade(self, trade_details: Dict[str, Any]):
        """
        Log detailed trade information
        """
        log_entry = {
            'event_id': str(uuid.uuid4()),
            'type': 'TRADE',
            **trade_details
        }
        logging.info(str(log_entry))
        
    def record_compliance_event(self, event: ComplianceEvent):
        """
        Record and log potential compliance violations
        """
        self.events.append(event)
        logging.warning(f"COMPLIANCE VIOLATION: {event}")

class PerformanceMonitor:
    """
    Track system-wide performance metrics
    """
    def __init__(self):
        self.metrics = {
            'total_trades': 0,
            'successful_trades': 0,
            'rejected_trades': 0,
            'average_latency_ms': 0,
            'total_latency': 0
        }
    
    def record_trade_performance(self, latency_ms: float, success: bool):
        """
        Update performance metrics for each trade
        """
        self.metrics['total_trades'] += 1
        self.metrics['total_latency'] += latency_ms
        self.metrics['average_latency_ms'] = (
            self.metrics['total_latency'] / self.metrics['total_trades']
        )
        
        if success:
            self.metrics['successful_trades'] += 1
        else:
            self.metrics['rejected_trades'] += 1
    
    def get_performance_report(self):
        """
        Generate performance report
        """
        success_rate = (
            self.metrics['successful_trades'] / self.metrics['total_trades']
        ) * 100 if self.metrics['total_trades'] > 0 else 0
        
        return {
            'total_trades': self.metrics['total_trades'],
            'success_rate': success_rate,
            'average_latency_ms': self.metrics['average_latency_ms']
        }

def main():
    audit_logger = AuditLogger()
    performance_monitor = PerformanceMonitor()
    
    # Simulate trading activity
    for _ in range(100):
        trade_details = {
            'instrument': 'AAPL',
            'quantity': 100,
            'price': 150.00,
            'timestamp': time.time()
        }
        
        start_time = time.time()
        success = True  # In real system, this would depend on trade execution
        
        audit_logger.log_trade(trade_details)
        performance_monitor.record_trade_performance(
            latency_ms=(time.time() - start_time) * 1000, 
            success=success
        )
    
    # Generate performance report
    performance_report = performance_monitor.get_performance_report()
    print("Performance Report:", performance_report)

if __name__ == '__main__':
    main()
