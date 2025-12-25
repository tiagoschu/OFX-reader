"""
Transfer Detection Helper
Detects internal transfers between accounts
"""

import pandas as pd
from datetime import timedelta


class TransferDetector:
    """Detects and pairs internal transfers between accounts"""

    def __init__(self, tolerance=1.0):
        """
        Initialize detector

        Args:
            tolerance: Maximum difference in value to consider a match (in R$)
        """
        self.tolerance = tolerance

    def detect_transfer_pairs(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect transfer pairs in transaction data

        A transfer pair is:
        - Same amount (within tolerance)
        - Same date or D+1
        - One debit, one credit
        - Different accounts

        Args:
            df: DataFrame with transactions

        Returns:
            DataFrame with 'is_internal_transfer' column added
        """
        if df.empty:
            return df

        # Add flag column
        df['is_internal_transfer'] = False
        df['transfer_pair_id'] = None

        # Convert dates if needed
        if 'data_dt' not in df.columns and 'data' in df.columns:
            df['data_dt'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')

        # Track which transactions have been paired
        paired_indices = set()
        pair_id = 0

        # Iterate through debits
        debits = df[df['valor'] < 0].copy()
        credits = df[df['valor'] > 0].copy()

        for debit_idx, debit_row in debits.iterrows():
            if debit_idx in paired_indices:
                continue

            debit_value = abs(debit_row['valor'])
            debit_date = debit_row['data_dt']
            debit_account = f"{debit_row.get('banco', '')}_{debit_row.get('conta', '')}"

            # Look for matching credit
            for credit_idx, credit_row in credits.iterrows():
                if credit_idx in paired_indices:
                    continue

                credit_value = credit_row['valor']
                credit_date = credit_row['data_dt']
                credit_account = f"{credit_row.get('banco', '')}_{credit_row.get('conta', '')}"

                # Check if it's a match
                if self._is_transfer_pair(
                    debit_value, credit_value,
                    debit_date, credit_date,
                    debit_account, credit_account
                ):
                    # Mark both as internal transfer
                    df.at[debit_idx, 'is_internal_transfer'] = True
                    df.at[credit_idx, 'is_internal_transfer'] = True
                    df.at[debit_idx, 'transfer_pair_id'] = pair_id
                    df.at[credit_idx, 'transfer_pair_id'] = pair_id

                    paired_indices.add(debit_idx)
                    paired_indices.add(credit_idx)
                    pair_id += 1
                    break

        return df

    def _is_transfer_pair(self, debit_value, credit_value, debit_date, credit_date,
                         debit_account, credit_account):
        """
        Check if two transactions form a transfer pair

        Args:
            debit_value: Absolute value of debit
            credit_value: Value of credit
            debit_date: Date of debit transaction
            credit_date: Date of credit transaction
            debit_account: Account identifier for debit
            credit_account: Account identifier for credit

        Returns:
            True if transactions are a transfer pair
        """
        # Check 1: Values must be equal (within tolerance)
        value_diff = abs(debit_value - credit_value)
        if value_diff > self.tolerance:
            return False

        # Check 2: Must be different accounts
        if debit_account == credit_account:
            return False

        # Check 3: Dates must be same day or D+1
        if pd.isna(debit_date) or pd.isna(credit_date):
            return False

        date_diff = abs((credit_date - debit_date).days)
        if date_diff > 1:
            return False

        return True

    def detect_unpaired_transfers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect transactions that look like transfers but weren't paired

        These are flagged for manual review

        Args:
            df: DataFrame with transactions (after detect_transfer_pairs)

        Returns:
            DataFrame with 'possible_transfer' column
        """
        if df.empty:
            return df

        df['possible_transfer'] = False

        # Keywords that suggest transfer
        transfer_keywords = ['pix', 'ted', 'doc', 'transferencia', 'transferência',
                            'transfer', 'conta global', 'entre contas']

        # Mark as possible transfer if:
        # - Has transfer keywords
        # - NOT already paired
        for idx, row in df.iterrows():
            if row.get('is_internal_transfer', False):
                continue

            desc = str(row.get('descricao', '')).lower()
            if any(keyword in desc for keyword in transfer_keywords):
                df.at[idx, 'possible_transfer'] = True

        return df

    def get_transfer_summary(self, df: pd.DataFrame) -> dict:
        """
        Get summary of transfer detection

        Args:
            df: DataFrame with transactions (after detection)

        Returns:
            Dict with transfer statistics
        """
        if df.empty:
            return {}

        paired = df[df.get('is_internal_transfer', False)]
        unpaired = df[df.get('possible_transfer', False)]

        # Count unique pairs
        num_pairs = paired['transfer_pair_id'].nunique() if 'transfer_pair_id' in paired.columns else 0

        summary = {
            'total_paired_transactions': len(paired),
            'total_transfer_pairs': num_pairs,
            'total_unpaired_possible': len(unpaired),
            'total_transfer_value': paired['valor'].abs().sum() / 2 if not paired.empty else 0,
        }

        return summary
