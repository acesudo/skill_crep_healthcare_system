"""Dataset splitting module implementing stratified multi-target partitioning.
"""

from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from .config import DataGenerationConfig


class DatasetSplitter:
    """Partitions the canonical dataset into Train (70%), Validation (15%), and Test (15%)
    splits with strict stratification across Category x Urgency combinations.
    """

    def __init__(self, config: DataGenerationConfig = DataGenerationConfig()):
        self.config = config

    def split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Executes a 2-stage stratified split:
        1. Split into 70% Train and 30% Temporary (Val + Test).
        2. Split 30% Temporary equally into 15% Val and 15% Test.
        """
        # Create composite stratification label
        df_strat = df.copy()
        df_strat["strat_key"] = df_strat["category"] + "_" + df_strat["urgency"]

        # Stage 1: 70% Train, 30% Temp (Val + Test)
        train_df, temp_df = train_test_split(
            df_strat,
            test_size=(self.config.val_ratio + self.config.test_ratio),
            random_state=self.config.random_seed,
            stratify=df_strat["strat_key"],
        )

        # Stage 2: Split Temp into 50/50 (which is 15% and 15% of total)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=0.50,
            random_state=self.config.random_seed,
            stratify=temp_df["strat_key"],
        )

        # Drop temporary stratification helper key
        train_df = train_df.drop(columns=["strat_key"]).reset_index(drop=True)
        val_df = val_df.drop(columns=["strat_key"]).reset_index(drop=True)
        test_df = test_df.drop(columns=["strat_key"]).reset_index(drop=True)

        return train_df, val_df, test_df
