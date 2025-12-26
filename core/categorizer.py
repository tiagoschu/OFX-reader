"""
Transaction Categorizer
Auto-categorizes transactions based on description keywords
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import CATEGORIES, CATEGORY_PRESETS
import pandas as pd


class TransactionCategorizer:
    """Categorizes transactions based on keywords in descriptions"""

    def __init__(self, custom_rules=None, category_preset=None):
        """
        Initialize categorizer

        Args:
            custom_rules: Dict of custom categorization rules
            category_preset: Name of category preset to use ('personal', 'business', 'travel_agency', etc.)
        """
        # Use specified preset or default
        if category_preset and category_preset in CATEGORY_PRESETS:
            self.categories = CATEGORY_PRESETS[category_preset]['categories'].copy()
        else:
            self.categories = CATEGORIES.copy()

        if custom_rules:
            self.categories.update(custom_rules)

    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a single transaction based on description

        Args:
            description: Transaction description

        Returns:
            Category name
        """
        if not description:
            return 'Outros'

        description_lower = description.lower()

        # Check each category's keywords
        for category_name, category_data in self.categories.items():
            keywords = category_data.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category_name

        # Default category
        return 'Outros'

    def categorize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add category column to dataframe

        Args:
            df: DataFrame with transactions

        Returns:
            DataFrame with 'categoria' column added
        """
        if df.empty:
            return df

        # Apply categorization
        df['categoria'] = df['descricao'].apply(self.categorize_transaction)

        # Add category color and icon
        df['categoria_cor'] = df['categoria'].map(
            lambda x: self.categories.get(x, {}).get('color', '#607D8B')
        )
        df['categoria_icone'] = df['categoria'].map(
            lambda x: self.categories.get(x, {}).get('icon', '📦')
        )

        return df

    def get_category_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary statistics by category

        Args:
            df: DataFrame with categorized transactions

        Returns:
            DataFrame with category summaries
        """
        if df.empty or 'categoria' not in df.columns:
            return pd.DataFrame()

        # Group by category
        summary = df.groupby('categoria').agg({
            'valor': ['count', 'sum'],
            'categoria_cor': 'first',
            'categoria_icone': 'first'
        }).reset_index()

        # Flatten column names
        summary.columns = ['categoria', 'qtd_transacoes', 'total', 'cor', 'icone']

        # Sort by total (absolute value)
        summary['total_abs'] = summary['total'].abs()
        summary = summary.sort_values('total_abs', ascending=False)
        summary = summary.drop('total_abs', axis=1)

        return summary

    def get_spending_by_category(self, df: pd.DataFrame, transaction_type='debit') -> pd.DataFrame:
        """
        Get spending or income by category

        Args:
            df: DataFrame with categorized transactions
            transaction_type: 'debit' for expenses, 'credit' for income

        Returns:
            DataFrame with category totals
        """
        if df.empty or 'categoria' not in df.columns:
            return pd.DataFrame()

        # Filter by transaction type
        if transaction_type == 'debit':
            filtered_df = df[df['valor'] < 0].copy()
            filtered_df['valor'] = filtered_df['valor'].abs()
        else:
            filtered_df = df[df['valor'] > 0].copy()

        # Group by category
        summary = filtered_df.groupby('categoria').agg({
            'valor': 'sum',
            'categoria_cor': 'first',
            'categoria_icone': 'first'
        }).reset_index()

        summary.columns = ['categoria', 'total', 'cor', 'icone']
        summary = summary.sort_values('total', ascending=False)

        return summary

    def add_custom_rule(self, category_name: str, keywords: list, color: str = None, icon: str = None):
        """
        Add or update a custom categorization rule

        Args:
            category_name: Name of the category
            keywords: List of keywords to match
            color: Optional color for the category
            icon: Optional icon for the category
        """
        if category_name not in self.categories:
            self.categories[category_name] = {}

        self.categories[category_name]['keywords'] = keywords

        if color:
            self.categories[category_name]['color'] = color
        if icon:
            self.categories[category_name]['icon'] = icon

    def remove_category(self, category_name: str):
        """Remove a custom category"""
        if category_name in self.categories and category_name != 'Outros':
            del self.categories[category_name]

    def get_all_categories(self) -> dict:
        """Get all categories with their metadata"""
        return self.categories.copy()
