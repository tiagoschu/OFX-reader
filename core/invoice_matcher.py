"""
Invoice Matcher - Match NFSe invoices with OFX receipts
Supports both Standard and Agency modes
"""

import pandas as pd
from datetime import timedelta
from utils.cpf_cnpj_validator import clean_cpf_cnpj


class InvoiceMatcher:
    """Match invoices with OFX transactions"""

    def __init__(self, tolerance_days=3, tolerance_percent=5.0, mode='standard'):
        """
        Initialize matcher

        Args:
            tolerance_days: Days tolerance for date matching (±N days)
            tolerance_percent: Percentage tolerance for value matching (±N%)
            mode: 'standard' or 'agency'
                - standard: Match by CPF + Date + Value (service providers)
                - agency: Match by CPF + Date only (travel agencies with markup)
        """
        self.tolerance_days = tolerance_days
        self.tolerance_percent = tolerance_percent / 100.0
        self.mode = mode
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
        if self.mode == 'agency':
            return self._match_agency_mode(invoices_df, ofx_df)
        else:
            return self._match_standard_mode(invoices_df, ofx_df)

    def _match_agency_mode(self, invoices_df, ofx_df):
        """
        Match in AGENCY mode: CPF + Date only (ignore value)

        Use case: Travel agencies where:
        - Invoice value = markup/commission (e.g., R$ 200)
        - OFX receipt = full payment from customer (e.g., R$ 1,200)
        - Value comparison doesn't make sense!
        """
        if invoices_df is None or invoices_df.empty:
            return invoices_df, pd.DataFrame(), {'total': 0, 'matched': 0, 'pending': 0}

        if ofx_df is None or ofx_df.empty:
            return invoices_df, pd.DataFrame(), {'total': len(invoices_df), 'matched': 0, 'pending': len(invoices_df)}

        # Ensure CPF/CNPJ column exists in OFX
        if 'cpf_cnpj' not in ofx_df.columns:
            print("[MATCHER] Warning: OFX data doesn't have 'cpf_cnpj' column. Enriching...")
            from core.ofx_enricher import enrich_ofx_data
            ofx_df = enrich_ofx_data(ofx_df)

        # Debug: Show CPF/CNPJ extraction stats
        ofx_with_cpf = ofx_df[ofx_df['cpf_cnpj'] != '']
        print(f"[MATCHER] OFX transactions with CPF/CNPJ: {len(ofx_with_cpf)} of {len(ofx_df)}")
        if not ofx_with_cpf.empty:
            print(f"[MATCHER] Sample OFX CPFs: {ofx_with_cpf['cpf_cnpj'].head(3).tolist()}")

        # Debug: Show invoice CPF/CNPJ stats
        inv_with_cpf = invoices_df[invoices_df['cpf_cnpj'] != '']
        print(f"[MATCHER] Invoices with CPF/CNPJ: {len(inv_with_cpf)} of {len(invoices_df)}")
        if not inv_with_cpf.empty:
            print(f"[MATCHER] Sample Invoice CPFs: {inv_with_cpf['cpf_cnpj'].head(3).tolist()}")

        # Prepare OFX data (only credits)
        ofx_receipts = ofx_df[ofx_df['valor'] > 0].copy()

        # Ensure data_dt column exists in OFX
        if 'data_dt' not in ofx_receipts.columns:
            print("[MATCHER] Creating data_dt column in OFX...")
            ofx_receipts['data_dt'] = pd.to_datetime(ofx_receipts['data'], format='%d/%m/%Y', errors='coerce')

        # Prepare invoices
        invoices = invoices_df.copy()

        # Ensure data_dt column exists in invoices
        if 'data_dt' not in invoices.columns:
            print("[MATCHER] Creating data_dt column in invoices...")
            invoices['data_dt'] = pd.to_datetime(invoices['data'], format='%d/%m/%Y', errors='coerce')

        # Store matches
        self.matches = []

        # Group by CPF/CNPJ for efficient matching
        print(f"[MATCHER] Starting agency mode matching for {len(invoices['cpf_cnpj'].unique())} unique CPFs...")

        for cpf_cnpj in invoices['cpf_cnpj'].unique():
            if not cpf_cnpj:
                continue

            # Get all invoices for this CPF
            cpf_invoices = invoices[invoices['cpf_cnpj'] == cpf_cnpj]

            # Get all OFX receipts for this CPF
            cpf_receipts = ofx_receipts[ofx_receipts['cpf_cnpj'] == cpf_cnpj]

            if cpf_receipts.empty:
                print(f"[MATCHER] CPF {cpf_cnpj}: {len(cpf_invoices)} invoices, 0 OFX receipts - NO MATCH")
                continue

            print(f"[MATCHER] CPF {cpf_cnpj}: {len(cpf_invoices)} invoices, {len(cpf_receipts)} OFX receipts")

            # Match each invoice with receipts from same CPF
            for inv_idx, invoice in cpf_invoices.iterrows():
                matches = self._find_matches_agency(invoice, cpf_receipts)

                if matches:
                    print(f"[MATCHER]   ✓ Invoice {invoice['numero']} matched with {len(matches)} payments")
                else:
                    print(f"[MATCHER]   ✗ Invoice {invoice['numero']} - no matches (date out of range?)")

                if matches:
                    # Update invoice
                    invoices.at[inv_idx, 'status'] = 'Vinculado'
                    invoices.at[inv_idx, 'match_count'] = len(matches)
                    invoices.at[inv_idx, 'valor_matched'] = sum(m['valor'] for m in matches)
                    invoices.at[inv_idx, 'match_ofx_ids'] = ','.join(str(m['ofx_id']) for m in matches)

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
                            'match_score': match['score']
                        })

        # Create matches DataFrame
        matches_df = pd.DataFrame(self.matches) if self.matches else pd.DataFrame()

        # Summary
        matched_count = len(invoices[invoices['status'] == 'Vinculado'])
        summary = {
            'total_invoices': len(invoices),
            'matched': matched_count,
            'pending': len(invoices) - matched_count,
            'total_value': invoices['valor_liquido'].sum(),
            'matched_value': invoices[invoices['status'] == 'Vinculado']['valor_matched'].sum(),
            'pending_value': invoices[invoices['status'] == 'Pendente']['valor_liquido'].sum()
        }

        return invoices, matches_df, summary

    def _find_matches_agency(self, invoice, ofx_receipts):
        """
        Find OFX receipts that match invoice (AGENCY mode)

        Criteria:
        - Same CPF/CNPJ (already filtered)
        - Date within tolerance
        - Ignore value!
        """
        matches = []

        invoice_date = invoice['data_dt']

        # Date range
        date_min = invoice_date - timedelta(days=self.tolerance_days)
        date_max = invoice_date + timedelta(days=self.tolerance_days)

        # Debug: Show date range
        print(f"[MATCHER]     Invoice date: {invoice['data']}, looking for payments between {date_min.strftime('%d/%m/%Y')} and {date_max.strftime('%d/%m/%Y')}")

        # Find candidates by date only
        candidates = ofx_receipts[
            (ofx_receipts['data_dt'] >= date_min) &
            (ofx_receipts['data_dt'] <= date_max)
        ]

        print(f"[MATCHER]     Found {len(candidates)} candidates within date range")

        for _, receipt in candidates.iterrows():
            score = self._calculate_match_score_agency(invoice, receipt)

            if score >= 60:  # CPF match is mandatory (60 points)
                days_diff = abs((receipt['data_dt'] - invoice_date).days)

                matches.append({
                    'ofx_id': receipt.name if hasattr(receipt, 'name') else receipt.get('ofx_id', 0),
                    'data': receipt['data'],
                    'valor': receipt['valor'],
                    'descricao': receipt.get('memo', '') or receipt.get('descricao', ''),
                    'days_diff': days_diff,
                    'score': score
                })

        # Sort by score (best matches first)
        matches.sort(key=lambda x: x['score'], reverse=True)

        return matches

    def _calculate_match_score_agency(self, invoice, receipt):
        """
        Calculate match score for AGENCY mode (0-100)

        Score weights:
        - CPF match: 60 points (mandatory)
        - Date proximity: 30 points
        - Name similarity: 10 points
        """
        score = 0

        # 1. CPF/CNPJ match (MANDATORY - 60 points)
        if invoice['cpf_cnpj'] == receipt['cpf_cnpj']:
            score += 60
        else:
            return 0  # No match without CPF

        # 2. Date proximity (30 points max)
        days_diff = abs((receipt['data_dt'] - invoice['data_dt']).days)

        if days_diff <= 5:
            score += 30
        elif days_diff <= 15:
            score += 20
        elif days_diff <= 35:
            score += 10
        elif days_diff <= 60:
            score += 5

        # 3. Name similarity (10 points) - optional
        invoice_name = str(invoice.get('nome_tomador', '')).lower()
        receipt_memo = str(receipt.get('memo', '')).lower()

        if invoice_name and invoice_name in receipt_memo:
            score += 10

        return score

    def _match_standard_mode(self, invoices_df, ofx_df):
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
