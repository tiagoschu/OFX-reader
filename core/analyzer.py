"""
Data Analyzer
Provides various analysis functions for transaction data
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import calendar


class DataAnalyzer:
    """Analyzes transaction data and provides insights"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with transaction data

        Args:
            df: DataFrame with transactions (must have 'data', 'valor', 'banco', 'conta', 'arquivo_origem' columns)
        """
        self.df = df.copy() if not df.empty else pd.DataFrame()

        if not self.df.empty and 'data' in self.df.columns:
            # Convert date strings to datetime for analysis
            self.df['data_dt'] = pd.to_datetime(self.df['data'], format='%d/%m/%Y', errors='coerce')

    def get_basic_stats(self) -> Dict:
        """Get basic statistics"""
        if self.df.empty:
            return {}

        stats = {
            'total_transacoes': len(self.df),
            'total_creditos': len(self.df[self.df['valor'] > 0]),
            'total_debitos': len(self.df[self.df['valor'] < 0]),
            'soma_creditos': float(self.df[self.df['valor'] > 0]['valor'].sum()),
            'soma_debitos': float(self.df[self.df['valor'] < 0]['valor'].sum()),
            'saldo_liquido': float(self.df['valor'].sum()),
            'ticket_medio_credito': float(self.df[self.df['valor'] > 0]['valor'].mean()) if len(self.df[self.df['valor'] > 0]) > 0 else 0,
            'ticket_medio_debito': float(self.df[self.df['valor'] < 0]['valor'].mean()) if len(self.df[self.df['valor'] < 0]) > 0 else 0,
            'maior_credito': float(self.df[self.df['valor'] > 0]['valor'].max()) if len(self.df[self.df['valor'] > 0]) > 0 else 0,
            'maior_debito': float(self.df[self.df['valor'] < 0]['valor'].min()) if len(self.df[self.df['valor'] < 0]) > 0 else 0,
        }

        return stats

    def get_monthly_summary(self) -> pd.DataFrame:
        """Get summary by month"""
        if self.df.empty or 'data_dt' not in self.df.columns:
            return pd.DataFrame()

        df_valid = self.df.dropna(subset=['data_dt'])

        if df_valid.empty:
            return pd.DataFrame()

        # Extract year-month
        df_valid['ano_mes'] = df_valid['data_dt'].dt.to_period('M')

        # Group by month
        monthly = df_valid.groupby('ano_mes').agg({
            'valor': ['count', 'sum'],
        }).reset_index()

        monthly.columns = ['mes', 'qtd_transacoes', 'total']

        # Separate credits and debits
        monthly_credits = df_valid[df_valid['valor'] > 0].groupby('ano_mes')['valor'].sum()
        monthly_debits = df_valid[df_valid['valor'] < 0].groupby('ano_mes')['valor'].sum()

        monthly['creditos'] = monthly['mes'].map(monthly_credits).fillna(0)
        monthly['debitos'] = monthly['mes'].map(monthly_debits).fillna(0)

        # Convert period to string for display
        monthly['mes_str'] = monthly['mes'].astype(str)

        return monthly

    def get_daily_pattern(self) -> pd.DataFrame:
        """Analyze transaction patterns by day of week"""
        if self.df.empty or 'data_dt' not in self.df.columns:
            return pd.DataFrame()

        df_valid = self.df.dropna(subset=['data_dt'])

        if df_valid.empty:
            return pd.DataFrame()

        # Get day of week (0=Monday, 6=Sunday)
        df_valid['dia_semana'] = df_valid['data_dt'].dt.dayofweek
        df_valid['dia_semana_nome'] = df_valid['data_dt'].dt.day_name()

        # Group by day of week
        daily = df_valid.groupby(['dia_semana', 'dia_semana_nome']).agg({
            'valor': ['count', 'sum']
        }).reset_index()

        daily.columns = ['dia_numero', 'dia_nome', 'qtd_transacoes', 'total']
        daily = daily.sort_values('dia_numero')

        return daily

    def detect_gaps(self) -> List[Dict]:
        """
        Detect missing periods (gaps) in transaction data by bank/account

        Returns:
            List of gaps with information about missing periods
        """
        if self.df.empty or 'data_dt' not in self.df.columns:
            return []

        df_valid = self.df.dropna(subset=['data_dt'])

        if df_valid.empty:
            return []

        gaps = []

        # Group by bank and account
        for (banco, conta), group in df_valid.groupby(['banco', 'conta']):
            # Sort by date
            group_sorted = group.sort_values('data_dt')

            # Get date range
            min_date = group_sorted['data_dt'].min()
            max_date = group_sorted['data_dt'].max()

            # Get all files for this account
            arquivos = group_sorted['arquivo_origem'].unique().tolist()

            # Check for monthly gaps
            current_date = min_date
            expected_months = []
            actual_months = set()

            while current_date <= max_date:
                expected_months.append((current_date.year, current_date.month))
                current_date = current_date + pd.DateOffset(months=1)

            # Get actual months with transactions
            for _, row in group_sorted.iterrows():
                actual_months.add((row['data_dt'].year, row['data_dt'].month))

            # Find missing months
            missing_months = [m for m in expected_months if m not in actual_months]

            for year, month in missing_months:
                month_name = calendar.month_name[month]

                # Check if there's a file for this period
                month_start = datetime(year, month, 1)
                month_end = datetime(year, month, calendar.monthrange(year, month)[1])

                # Simple heuristic: check if any file might cover this period
                # (In a real scenario, we'd need to parse file metadata)
                has_potential_file = any(
                    f"{year:04d}" in arquivo and f"{month:02d}" in arquivo
                    for arquivo in arquivos
                )

                gap_info = {
                    'banco': banco,
                    'conta': conta,
                    'ano': year,
                    'mes': month,
                    'mes_nome': f"{month_name}/{year}",
                    'data_inicio': month_start.strftime('%d/%m/%Y'),
                    'data_fim': month_end.strftime('%d/%m/%Y'),
                    'tem_arquivo': has_potential_file,
                    'severidade': 'baixa' if has_potential_file else 'alta',
                    'mensagem': 'Período sem transações (arquivo presente)' if has_potential_file else '⚠️ Possível mês esquecido - arquivo OFX não encontrado'
                }

                gaps.append(gap_info)

        return gaps

    def get_bank_distribution(self) -> pd.DataFrame:
        """Get transaction distribution by bank"""
        if self.df.empty:
            return pd.DataFrame()

        bank_dist = self.df.groupby('banco').agg({
            'valor': ['count', 'sum']
        }).reset_index()

        bank_dist.columns = ['banco', 'qtd_transacoes', 'total']
        bank_dist = bank_dist.sort_values('total', ascending=False)

        return bank_dist

    def get_top_transactions(self, n=10, transaction_type='all') -> pd.DataFrame:
        """
        Get top N transactions by value

        Args:
            n: Number of transactions to return
            transaction_type: 'all', 'credit', or 'debit'
        """
        if self.df.empty:
            return pd.DataFrame()

        if transaction_type == 'credit':
            filtered = self.df[self.df['valor'] > 0].copy()
            filtered = filtered.nlargest(n, 'valor')
        elif transaction_type == 'debit':
            filtered = self.df[self.df['valor'] < 0].copy()
            filtered = filtered.nsmallest(n, 'valor')
        else:
            # Get top by absolute value
            df_copy = self.df.copy()
            df_copy['valor_abs'] = df_copy['valor'].abs()
            filtered = df_copy.nlargest(n, 'valor_abs')
            filtered = filtered.drop('valor_abs', axis=1)

        return filtered

    def get_recurrent_transactions(self, threshold=3) -> pd.DataFrame:
        """
        Identify potentially recurrent transactions

        Args:
            threshold: Minimum number of occurrences to be considered recurrent
        """
        if self.df.empty:
            return pd.DataFrame()

        # Group by description and value (with small tolerance)
        df_copy = self.df.copy()
        df_copy['valor_round'] = df_copy['valor'].round(2)

        recurrent = df_copy.groupby(['descricao', 'valor_round']).agg({
            'valor': 'count',
            'data': ['min', 'max']
        }).reset_index()

        recurrent.columns = ['descricao', 'valor', 'frequencia', 'primeira_data', 'ultima_data']

        # Filter by threshold
        recurrent = recurrent[recurrent['frequencia'] >= threshold]
        recurrent = recurrent.sort_values('frequencia', ascending=False)

        return recurrent

    def get_date_range(self) -> Tuple[str, str]:
        """Get min and max dates in dataset"""
        if self.df.empty or 'data_dt' not in self.df.columns:
            return ('', '')

        df_valid = self.df.dropna(subset=['data_dt'])

        if df_valid.empty:
            return ('', '')

        min_date = df_valid['data_dt'].min().strftime('%d/%m/%Y')
        max_date = df_valid['data_dt'].max().strftime('%d/%m/%Y')

        return (min_date, max_date)
