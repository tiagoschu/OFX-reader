"""
CSV Template Generator and Parser
Handles import/export of custom category plans and DRE structures
"""

import csv
import os
from pathlib import Path


class CSVTemplates:
    """Generate and parse CSV templates for categories and DRE"""

    @staticmethod
    def get_templates_dir():
        """Get templates directory"""
        home = Path.home()
        templates_dir = home / "OFX-Templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        return str(templates_dir)

    @staticmethod
    def generate_categories_template(filepath=None):
        """
        Generate CSV template for categories

        Format:
        Nome, Tipo, Ícone, Keywords (separadas por ;), Código
        """
        if not filepath:
            filepath = os.path.join(
                CSVTemplates.get_templates_dir(),
                "template_categorias.csv"
            )

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['Nome', 'Tipo', 'Ícone', 'Keywords', 'Código', 'Cor'])

            # Examples
            writer.writerow([
                '4-01-001 Receitas de Comissões',
                'revenue',
                '💰',
                'receita comissao;comissao recebida;comissão',
                '4-01-001',
                '#4CAF50'
            ])
            writer.writerow([
                '3-02-002 Despesas com Pessoal',
                'expense',
                '👥',
                'salario;folha;funcionario;salário',
                '3-02-002',
                '#E57373'
            ])
            writer.writerow([
                '3-02-001 Aluguéis e Condomínios',
                'expense',
                '🏠',
                'aluguel;condominio;condomínio;locação',
                '3-02-001',
                '#EF5350'
            ])

        return filepath

    @staticmethod
    def generate_dre_template(filepath=None):
        """
        Generate CSV template for DRE structure

        Format:
        Chave, Label, Tipo, É Total?, Cor, Categorias/Fórmula
        """
        if not filepath:
            filepath = os.path.join(
                CSVTemplates.get_templates_dir(),
                "template_dre.csv"
            )

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['Chave', 'Label', 'Tipo', 'É Total?', 'Cor', 'Categorias/Fórmula'])

            # Examples
            writer.writerow([
                'receita_bruta',
                'RECEITA BRUTA',
                'revenue',
                'SIM',
                '#4CAF50',
                'Receitas;Vendas;4-01'
            ])
            writer.writerow([
                'deducoes',
                '(-) Deduções',
                'expense',
                'NÃO',
                '',
                'Deduções;Impostos sobre Vendas'
            ])
            writer.writerow([
                'receita_liquida',
                '(=) RECEITA LÍQUIDA',
                'calculated',
                'SIM',
                '#66BB6A',
                'receita_bruta - deducoes'
            ])

        return filepath

    @staticmethod
    def parse_categories_csv(filepath):
        """
        Parse categories CSV file

        Returns:
            dict: Categories in the format {name: {keywords, color, icon, type, code}}
        """
        categories = {}

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                name = row.get('Nome', '').strip()
                if not name:
                    continue

                # Parse keywords (separated by ;)
                keywords_str = row.get('Keywords', '')
                keywords = [kw.strip() for kw in keywords_str.split(';') if kw.strip()]

                categories[name] = {
                    'keywords': keywords,
                    'color': row.get('Cor', '#757575').strip() or '#757575',
                    'icon': row.get('Ícone', '📁').strip() or '📁',
                    'type': row.get('Tipo', 'other').strip() or 'other',
                    'code': row.get('Código', '').strip()
                }

        return categories

    @staticmethod
    def parse_dre_csv(filepath):
        """
        Parse DRE structure CSV file

        Returns:
            dict: DRE structure with title and items list
        """
        items = []

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                key = row.get('Chave', '').strip()
                label = row.get('Label', '').strip()

                if not key or not label:
                    continue

                item_type = row.get('Tipo', '').strip().lower()
                is_total = row.get('É Total?', '').strip().upper() in ['SIM', 'YES', 'TRUE', '1']
                color = row.get('Cor', '').strip() or None
                categories_formula = row.get('Categorias/Fórmula', '').strip()

                item = {
                    'key': key,
                    'label': label,
                    'type': item_type,
                    'is_total': is_total,
                }

                if color:
                    item['color'] = color

                # Parse categories or formula
                if item_type == 'calculated':
                    # It's a formula
                    item['formula_str'] = categories_formula
                else:
                    # It's categories list
                    categories = [cat.strip() for cat in categories_formula.split(';') if cat.strip()]
                    item['categories'] = categories

                items.append(item)

        # Extract filename without extension as title
        filename = os.path.basename(filepath)
        title = os.path.splitext(filename)[0].replace('_', ' ').title()

        return {
            'title': f'DRE - {title}',
            'items': items
        }

    @staticmethod
    def export_categories_to_csv(categories, filepath):
        """
        Export categories dict to CSV file

        Args:
            categories: Dict with categories
            filepath: Output file path
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['Nome', 'Tipo', 'Ícone', 'Keywords', 'Código', 'Cor'])

            # Data
            for name, data in sorted(categories.items()):
                keywords_str = ';'.join(data.get('keywords', []))
                writer.writerow([
                    name,
                    data.get('type', 'other'),
                    data.get('icon', '📁'),
                    keywords_str,
                    data.get('code', ''),
                    data.get('color', '#757575')
                ])

    @staticmethod
    def export_dre_to_csv(dre_structure, filepath):
        """
        Export DRE structure to CSV file

        Args:
            dre_structure: Dict with title and items
            filepath: Output file path
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['Chave', 'Label', 'Tipo', 'É Total?', 'Cor', 'Categorias/Fórmula'])

            # Data
            for item in dre_structure.get('items', []):
                is_total_str = 'SIM' if item.get('is_total', False) else 'NÃO'
                color = item.get('color', '')

                # Get categories or formula
                if item.get('type') == 'calculated':
                    cat_formula = item.get('formula_str', '')
                else:
                    categories = item.get('categories', [])
                    cat_formula = ';'.join(categories)

                writer.writerow([
                    item.get('key', ''),
                    item.get('label', ''),
                    item.get('type', ''),
                    is_total_str,
                    color,
                    cat_formula
                ])
