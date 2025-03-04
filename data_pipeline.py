import kafka
from typing import Dict, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass

class DataNormalizer:
    """
    Normalize and clean market data from various sources
    """
    @staticmethod
    def normalize_market_data(raw_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert raw market data into standardized DataFrame
        
        Handles different exchange protocols and data formats
        """
        normalized_data = pd.DataFrame(raw_data)
        
        # Basic cleaning and transformation
        normalized_data['timestamp'] = pd.to_datetime(normalized_data['timestamp'])
        normalized_data['price'] = normalized_data['price'].astype(float)
        normalized_data['volume'] = normalized_data['volume'].astype(int)
        
        return normalized_data

class TechnicalIndicators:
    """
    Calculate real-time technical indicators
    """
    @staticmethod
    def moving_average(data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Compute moving average with configurable window"""
        return data['price'].rolling(window=window).mean()
    
    @staticmethod
    def relative_strength_index(data: pd.DataFrame, periods: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = data['price'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

class DataStreamProcessor:
    """
    Process market data streams using Apache Kafka and Flink-like processing
    """
    def __init__(self, kafka_bootstrap_servers: list):
        self.kafka_consumer = kafka.KafkaConsumer(
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset='earliest'
        )
    
    def consume_market_data(self, topic: str):
        """
        Consume market data from Kafka topic
        Simulates stream processing logic
        """
        self.kafka_consumer.subscribe([topic])
        
        for message in self.kafka_consumer:
            raw_data = message.value
            normalized_data = DataNormalizer.normalize_market_data(raw_data)
            
            # Compute real-time indicators
            ma_20 = TechnicalIndicators.moving_average(normalized_data)
            rsi_14 = TechnicalIndicators.relative_strength_index(normalized_data)
            
            yield {
                'normalized_data': normalized_data,
                'moving_average_20': ma_20,
                'rsi_14': rsi_14
            }

# Example usage demonstrating the data pipeline
def main():
    kafka_servers = ['localhost:9092']
    stream_processor = DataStreamProcessor(kafka_servers)
    
    for processed_data in stream_processor.consume_market_data('market_data_feed'):
        # Potential strategy logic or further processing
        print(processed_data)

if __name__ == '__main__':
    main()
