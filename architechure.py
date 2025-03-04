import typing
from dataclasses import dataclass
from enum import Enum, auto

class ExchangeProtocol(Enum):
    FIX = auto()
    ITCH = auto()
    OUCH = auto()

class MarketInstrumentType(Enum):
    STOCK = auto()
    DERIVATIVE = auto()
    FOREX = auto()
    FUTURES = auto()

@dataclass
class MarketDataSource:
    name: str
    protocol: ExchangeProtocol
    instruments: typing.List[MarketInstrumentType]
    data_feed_rate: int  # quotes per second

@dataclass
class SystemArchitecture:
    """
    High-Frequency Trading System Core Architecture
    
    Manages end-to-end trading infrastructure from data ingestion 
    to execution and monitoring.
    """
    data_sources: typing.List[MarketDataSource]
    streaming_platform: str  # e.g., Apache Kafka
    processing_engines: typing.List[str]  # e.g., Flink, Spark Streaming
    strategy_language: str  # Core logic language
    risk_management_enabled: bool
    compliance_checks: typing.List[str]

# Example instantiation
hft_system = SystemArchitecture(
    data_sources=[
        MarketDataSource(
            name="YahooFinance", 
            protocol=ExchangeProtocol.FIX,
            instruments=[
                MarketInstrumentType.STOCK, 
                MarketInstrumentType.FOREX
            ],
            data_feed_rate=1_000_000
        )
    ],
    streaming_platform="Apache Kafka",
    processing_engines=["Apache Flink", "Spark Streaming"],
    strategy_language="C++",
    risk_management_enabled=True,
    compliance_checks=["MiFID II", "SEC Regulations"]
)
