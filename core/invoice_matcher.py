"""
Invoice Matcher - Match NFSe invoices with OFX receipts
"""

import pandas as pd
from datetime import timedelta
from utils.cpf_cnpj_validator import clean_cpf_cnpj


class InvoiceMatcher:
    """Match invoices with OFX transactions"""

    def __init__(self, tolerance_days=3, tolerance_percent=5.0):
        """
        Initialize matcher

        Args:
            tolerance_days: Days tolerance for date matching (±N days)
            tolerance_percent: Percentage tolerance for value matching (±N%)
        """
        self.tolerance_days = tolerance_days
        self.tolerance_percent = tolerance_percent / 100.0
        self.matches = []

    def match(self, invoices_df, ofx_df):
        """
        Match invoices with OFX transactions

        Args:
            invoices_df: DataFrame with invoices
            ofx_df: DataFrame with OFX transactions

        Returns:
            tuple: (invoices_df_updated, matches_df, summary)
        """
        if invoices_df is None or invoices_df.empty:
            return invoices_df, pd.DataFrame(), {'total': 0, 'matched': 0, 'pending': 0}

        if ofx_df is None or ofx_df.empty:
            return invoices_df, pd.DataFrame(), {'total': len(invoices_df), 'matched': 0, 'pending': len(invoices_df)}

        # Prepare OFX data
        ofx_receipts = self._prepare_ofx_data(ofx_df)

        # Prepare invoices
        invoices = invoices_df.copy()

        # Store matches
        self.matches = []

        # Match each invoice
        for idx, invoice in invoices.iterrows():
            matches = self._find_matches(invoice, ofx_receipts)

            if matches:
                # Update invoice status
                invoices.at[idx, 'status'] = 'Pago' if self._is_fully_paid(invoice, matches) else 'Parcial'
                invoices.at[idx, 'match_count'] = len(matches)
                invoices.at[idx, 'valor_matched'] = sum(m['valor'] for m in matches)
                invoices.at[idx, 'match_ofx_ids'] = ','.join(str(m['ofx_id']) for m in matches)

                # Store match details
                for match in matches:
                    self.matches.append({
                        'invoice_numero': invoice['numero'],
                        'invoice_data': invoice['data'],
                        'invoice_valor': invoice['valor_liquido'],
                        'invoice_cpf_cnpj': invoice['cpf_cnpj'],
                        'invoice_nome': invoice['nome_tomador'],
                        'ofx_id': match['ofx_id'],
                        'ofx_data': match['data'],
                        'ofx_valor': match['valor'],
                        'ofx_descricao': match['descricao'],
                        'days_diff': match['days_diff'],
                        'value_diff_percent': match['value_diff_percent'],
                        'match_score': match['score']
                    })
            else:
                invoices.at[idx, 'status'] = 'Pendente'
                invoices.at[idx, 'match_count'] = 0
                invoices.at[idx, 'valor_matched'] = 0.0

        # Create matches DataFrame
        matches_df = pd.DataFrame(self.matches) if self.matches else pd.DataFrame()

        # Summary
        summary = {
            'total_invoices': len(invoices),
            'matched': len(invoices[invoices['status'].isin(['Pago', 'Parcial'])]),
            'pending': len(invoices[invoices['status'] == 'Pendente']),
            'total_value': invoices['valor_liquido'].sum(),
            'matched_value': invoices['valor_matched'].sum(),
            'pending_value': invoices[invoices['status'] == 'Pendente']['valor_liquido'].sum()
        }

        return invoices, matches_df, summary

    def _prepare_ofx_data(self, ofx_df):
        """
        Prepare OFX data for matching (only receipts/credits)

        Args:
            ofx_df: Original OFX DataFrame

        Returns:
            DataFrame: Prepared receipts data
        """
        # Only positive values (receipts)
        receipts = ofx_df[ofx_df['valor'] > 0].copy()

        # Ensure data_dt column
        if 'data_dt' not in receipts.columns:
            receipts['data_dt'] = pd.to_datetime(receipts['data'], format='%d/%m/%Y', errors='coerce')

        # Add ID if not present
        if receipts.index.name != 'ofx_id':
            receipts = receipts.reset_index(drop=True)
            receipts['ofx_id'] = receipts.index

        # Extract CPF/CNPJ from memo if present
        if 'memo' in receipts.columns:
            receipts['memo_cpf_cnpj'] = receipts['memo'].apply(self._extract_cpf_cnpj_from_text)
        else:
            receipts['memo_cpf_cnpj'] = None

        return receipts

    def _extract_cpf_cnpj_from_text(self, text):
        """Extract CPF/CNPJ from transaction description"""
        if not text or pd.isna(text):
            return None

        import re
        text = str(text)

        # Try to find CPF pattern (###.###.###-## or 11 digits)
        cpf_pattern = r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}'
        cpf_match = re.search(cpf_pattern, text)
        if cpf_match:
            return clean_cpf_cnpj(cpf_match.group())

        # Try to find CNPJ pattern (##.###.###/####-## or 14 digits)
        cnpj_pattern = r'\d{2}\.?\d{3}\.?\d{3}/?\\d{4}-?\d{2}'
        cnpj_match = re.search(cnpj_pattern, text)
        if cnpj_match:
            return clean_cpf_cnpj(cnpj_match.group())

        return None

    def _find_matches(self, invoice, ofx_receipts):
        """
        Find OFX receipts that match an invoice

        Args:
            invoice: Invoice row
            ofx_receipts: DataFrame with OFX receipts

        Returns:
            list: List of matching receipts with scores
        """
        matches = []

        invoice_date = invoice['data_dt']
        invoice_value = invoice['valor_liquido']
        invoice_cpf = invoice['cpf_cnpj']

        # Date range
        date_min = invoice_date - timedelta(days=self.tolerance_days)
        date_max = invoice_date + timedelta(days=self.tolerance_days)

        # Value range
        value_min = invoice_value * (1 - self.tolerance_percent)
        value_max = invoice_value * (1 + self.tolerance_percent)

        # Find candidates
        candidates = ofx_receipts[
            (ofx_receipts['data_dt'] >= date_min) &
            (ofx_receipts['data_dt'] <= date_max) &
            (ofx_receipts['valor'] >= value_min) &
            (ofx_receipts['valor'] <= value_max)
        ]

        for _, receipt in candidates.iterrows():
            score = self._calculate_match_score(invoice, receipt)

            if score > 0:
                days_diff = abs((receipt['data_dt'] - invoice_date).days)
                value_diff = abs(receipt['valor'] - invoice_value)
                value_diff_percent = (value_diff / invoice_value) * 100 if invoice_value > 0 else 0

                matches.append({
                    'ofx_id': receipt['ofx_id'],
                    'data': receipt['data'],
                    'valor': receipt['valor'],
                    'descricao': receipt.get('memo', '') or receipt.get('descricao', ''),
                    'days_diff': days_diff,
                    'value_diff': value_diff,
                    'value_diff_percent': value_diff_percent,
                    'score': score
                })

        # Sort by score (best matches first)
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches

    def _calculate_match_score(self, invoice, receipt):
        """
        Calculate match score (0-100)

        Args:
            invoice: Invoice row
            receipt: OFX receipt row

        Returns:
            float: Match score (0-100)
        """
        score = 0

        # 1. Exact CPF/CNPJ match (+40 points)
        invoice_cpf = invoice['cpf_cnpj']
        receipt_cpf = receipt.get('memo_cpf_cnpj')

        if receipt_cpf and invoice_cpf == receipt_cpf:
            score += 40

        # 2. Value proximity (+30 points max)
        invoice_value = invoice['valor_liquido']
        receipt_value = receipt['valor']
        value_diff_percent = abs(receipt_value - invoice_value) / invoice_value if invoice_value > 0 else 1

        if value_diff_percent <= 0.01:  # 1% diff
            score += 30
        elif value_diff_percent <= 0.03:  # 3% diff
            score += 20
        elif value_diff_percent <= 0.05:  # 5% diff
            score += 10

        # 3. Date proximity (+30 points max)
        days_diff = abs((receipt['data_dt'] - invoice['data_dt']).days)

        if days_diff == 0:  # Same day
            score += 30
        elif days_diff == 1:  # 1 day diff
            score += 20
        elif days_diff <= 2:  # 2 days diff
            score += 10
        elif days_diff <= 3:  # 3 days diff
            score += 5

        # Minimum score to consider a match
        return score if score >= 20 else 0

    def _is_fully_paid(self, invoice, matches):
        """Check if invoice is fully paid"""
        invoice_value = invoice['valor_liquido']
        matched_value = sum(m['valor'] for m in matches)

        # Consider fully paid if within 1% tolerance
        return abs(matched_value - invoice_value) / invoice_value <= 0.01 if invoice_value > 0 else False

    def analyze_by_customer(self, invoices_df, ofx_df=None):
        """
        Analyze invoices grouped by customer

        Args:
            invoices_df: DataFrame with invoices
            ofx_df: Optional DataFrame with OFX data

        Returns:
            DataFrame: Summary by customer (CPF/CNPJ)
        """
        if invoices_df is None or invoices_df.empty:
            return pd.DataFrame()

        # Group by customer
        summary = invoices_df.groupby('cpf_cnpj').agg({
            'numero': 'count',
            'valor_liquido': 'sum',
            'valor_matched': 'sum',
            'nome_tomador': 'first',
            'cpf_cnpj_formatted': 'first'
        }).reset_index()

        summary.columns = ['cpf_cnpj', 'qtd_notas', 'total_emitido', 'total_recebido', 'nome', 'cpf_cnpj_fmt']

        # Calculate pending
        summary['total_pendente'] = summary['total_emitido'] - summary['total_recebido']
        summary['percent_recebido'] = (summary['total_recebido'] / summary['total_emitido'] * 100).round(2)

        # Sort by pending value
        summary = summary.sort_values('total_pendente', ascending=False)

        return summary

    def analyze_by_month(self, invoices_df, ofx_df=None):
        """
        Analyze invoices grouped by month

        Args:
            invoices_df: DataFrame with invoices
            ofx_df: Optional DataFrame with OFX data

        Returns:
            DataFrame: Summary by month
        """
        if invoices_df is None or invoices_df.empty:
            return pd.DataFrame()

        # Extract year-month
        invoices = invoices_df.copy()
        invoices['ano_mes'] = invoices['data_dt'].dt.to_period('M')

        # Group by month
        summary = invoices.groupby('ano_mes').agg({
            'numero': 'count',
            'valor_liquido': 'sum',
            'valor_matched': 'sum'
        }).reset_index()

        summary.columns = ['mes', 'qtd_notas', 'total_emitido', 'total_recebido']

        # Calculate pending
        summary['total_pendente'] = summary['total_emitido'] - summary['total_recebido']
        summary['percent_recebido'] = (summary['total_recebido'] / summary['total_emitido'] * 100).round(2)

        # Convert period to string
        summary['mes'] = summary['mes'].astype(str)

        return summary
