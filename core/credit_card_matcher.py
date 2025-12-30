"""
Credit Card Matcher - Match credit card installments with OFX receipts
"""

import pandas as pd
from datetime import timedelta


class CreditCardMatcher:
    """Match credit card installments with OFX transactions"""

    def __init__(self, date_tolerance_days=5, value_tolerance=0.10):
        """
        Initialize matcher

        Args:
            date_tolerance_days: Days tolerance for date matching (±N days)
            value_tolerance: Value tolerance for matching (±R$)
        """
        self.date_tolerance_days = date_tolerance_days
        self.value_tolerance = value_tolerance
        self.matches = []

    def match(self, installments_df, ofx_df):
        """
        Match installments with OFX transactions

        Args:
            installments_df: DataFrame with credit card installments
            ofx_df: DataFrame with OFX transactions

        Returns:
            tuple: (installments_df_updated, matches_df, summary)
        """
        if installments_df is None or installments_df.empty:
            return installments_df, pd.DataFrame(), self._empty_summary()

        if ofx_df is None or ofx_df.empty:
            print("[CARD-MATCHER] Aviso: Nenhuma transação OFX disponível")
            return installments_df, pd.DataFrame(), self._empty_summary()

        print(f"[CARD-MATCHER] Iniciando matching de {len(installments_df)} parcelas com {len(ofx_df)} transações OFX")

        # Prepare OFX data (only credits)
        ofx_credits = ofx_df[ofx_df['valor'] > 0].copy()
        print(f"[CARD-MATCHER] Créditos OFX disponíveis: {len(ofx_credits)}")

        # Ensure data_dt column exists in OFX
        if 'data_dt' not in ofx_credits.columns:
            ofx_credits['data_dt'] = pd.to_datetime(ofx_credits['data'], format='%d/%m/%Y', errors='coerce')

        # Copy installments for updating
        installments = installments_df.copy()

        # Ensure data_prevista_dt column
        if 'data_prevista_dt' not in installments.columns:
            installments['data_prevista_dt'] = pd.to_datetime(installments['data_prevista'], errors='coerce')

        # Match each installment
        matched_count = 0
        for idx, installment in installments.iterrows():
            match_result = self._find_ofx_match(installment, ofx_credits)

            if match_result:
                # Update installment
                installments.at[idx, 'status_vinculacao'] = 'Vinculado'
                installments.at[idx, 'ofx_id'] = match_result['ofx_id']
                installments.at[idx, 'ofx_data'] = match_result['ofx_data']
                installments.at[idx, 'ofx_valor'] = match_result['ofx_valor']
                installments.at[idx, 'diferenca_dias'] = match_result['diferenca_dias']
                installments.at[idx, 'diferenca_valor'] = match_result['diferenca_valor']

                # Store match details
                self.matches.append(match_result)
                matched_count += 1

        # Create matches DataFrame
        matches_df = pd.DataFrame(self.matches) if self.matches else pd.DataFrame()

        # Summary
        summary = {
            'total_parcelas': len(installments),
            'vinculadas': matched_count,
            'pendentes': len(installments) - matched_count,
            'valor_total': installments['valor'].sum(),
            'valor_vinculado': installments[installments['status_vinculacao'] == 'Vinculado']['valor'].sum(),
            'valor_pendente': installments[installments['status_vinculacao'] == 'Pendente']['valor'].sum()
        }

        print(f"[CARD-MATCHER] Matching concluído: {matched_count} de {len(installments)} parcelas vinculadas")

        return installments, matches_df, summary

    def _find_ofx_match(self, installment, ofx_credits):
        """
        Find OFX transaction that matches installment

        Criteria:
        - Value within tolerance (±R$ 0.10)
        - Date within tolerance (±5 days)

        Args:
            installment: Installment row
            ofx_credits: DataFrame with OFX credits

        Returns:
            dict: Match details or None
        """
        valor_parcela = installment['valor']
        data_prevista = installment['data_prevista_dt']

        if pd.isna(data_prevista):
            return None

        # Filter by value tolerance
        valor_min = valor_parcela - self.value_tolerance
        valor_max = valor_parcela + self.value_tolerance

        value_matches = ofx_credits[
            (ofx_credits['valor'] >= valor_min) &
            (ofx_credits['valor'] <= valor_max)
        ]

        if value_matches.empty:
            return None

        # Filter by date tolerance
        data_min = data_prevista - timedelta(days=self.date_tolerance_days)
        data_max = data_prevista + timedelta(days=self.date_tolerance_days)

        full_matches = value_matches[
            (value_matches['data_dt'] >= data_min) &
            (value_matches['data_dt'] <= data_max)
        ]

        if full_matches.empty:
            return None

        # Multiple matches - use first occurrence
        if len(full_matches) > 1:
            print(f"[CARD-MATCHER] AVISO: Múltiplos matches encontrados para parcela {installment['venda_id']} #{installment['numero_parcela']}")
            print(f"[CARD-MATCHER]   Valor esperado: R$ {valor_parcela:.2f}")
            print(f"[CARD-MATCHER]   Data esperada: {data_prevista.strftime('%d/%m/%Y')}")
            print(f"[CARD-MATCHER]   Matches encontrados: {len(full_matches)}")
            for i, (_, match) in enumerate(full_matches.head(3).iterrows()):
                print(f"[CARD-MATCHER]     {i+1}. Data: {match['data']} | Valor: R$ {match['valor']:.2f} | {match.get('descricao', '')[:40]}")
            print(f"[CARD-MATCHER]   Usando PRIMEIRA OCORRÊNCIA")

        # Get first match
        best_match = full_matches.iloc[0]

        # Calculate differences
        diferenca_dias = abs((best_match['data_dt'] - data_prevista).days)
        diferenca_valor = abs(best_match['valor'] - valor_parcela)

        match_result = {
            'venda_id': installment['venda_id'],
            'numero_parcela': installment['numero_parcela'],
            'valor_parcela': valor_parcela,
            'data_prevista': data_prevista.strftime('%d/%m/%Y'),
            'ofx_id': best_match.get('id_transacao', ''),
            'ofx_data': best_match['data'],
            'ofx_valor': best_match['valor'],
            'ofx_descricao': best_match.get('descricao', best_match.get('memo', '')),
            'diferenca_dias': diferenca_dias,
            'diferenca_valor': round(diferenca_valor, 2),
            'adquirente': installment.get('adquirente', ''),
            'bandeira': installment.get('bandeira', ''),
            'estabelecimento': installment.get('estabelecimento', '')
        }

        return match_result

    def _empty_summary(self):
        """Return empty summary"""
        return {
            'total_parcelas': 0,
            'vinculadas': 0,
            'pendentes': 0,
            'valor_total': 0.0,
            'valor_vinculado': 0.0,
            'valor_pendente': 0.0
        }
