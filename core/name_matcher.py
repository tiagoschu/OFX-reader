"""
Name Matcher - Fuzzy matching for names in OFX descriptions
"""

import re
from typing import List, Tuple


class NameMatcher:
    """Utility for matching partial names in OFX descriptions"""

    # Common prepositions and articles to ignore
    STOPWORDS = {
        'de', 'da', 'do', 'dos', 'das',
        'e', 'o', 'a', 'os', 'as',
        'pix', 'ted', 'recebido', 'recebida', 'enviado', 'enviada',
        'transferencia', 'transferência', 'pagamento'
    }

    @staticmethod
    def extract_name_from_ofx_description(description: str) -> str:
        """
        Extract name from OFX description

        Examples:
            "Pix recebido de HEBERTON BRAVO" -> "HEBERTON BRAVO"
            "TED RECEBIDA - JOAO SILVA" -> "JOAO SILVA"
            "PIX ENVIADO PARA MARIA SANTOS" -> "MARIA SANTOS"

        Args:
            description: OFX transaction description

        Returns:
            Extracted name or original description if no pattern found
        """
        if not description:
            return ""

        description = description.upper().strip()

        # Common patterns to extract names
        patterns = [
            r'PIX\s+(?:RECEBIDO|RECEBIDA)\s+(?:DE|DA|DO)\s+(.+)',
            r'TED\s+(?:RECEBIDO|RECEBIDA)\s+(?:DE|DA|DO|-)\s+(.+)',
            r'TRANSFERENCIA\s+(?:RECEBIDO|RECEBIDA)\s+(?:DE|DA|DO)\s+(.+)',
            r'(?:DE|DA|DO)\s+([A-Z\s]+?)(?:\s*-\s*|$)',  # Generic "DE NOME"
        ]

        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                # Remove trailing punctuation and numbers
                extracted = re.sub(r'[^A-Z\s]', '', extracted).strip()
                if extracted:
                    return extracted

        # If no pattern matched, return cleaned description
        return re.sub(r'[^A-Z\s]', '', description).strip()

    @staticmethod
    def get_significant_words(text: str, min_length: int = 3) -> List[str]:
        """
        Get significant words from text (excluding stopwords and short words)

        Args:
            text: Input text
            min_length: Minimum word length to consider

        Returns:
            List of significant words in uppercase
        """
        if not text:
            return []

        text = text.upper().strip()
        words = text.split()

        significant = []
        for word in words:
            word_clean = re.sub(r'[^A-Z]', '', word)
            if (len(word_clean) >= min_length and
                word_clean.lower() not in NameMatcher.STOPWORDS):
                significant.append(word_clean)

        return significant

    @staticmethod
    def match_names(ofx_description: str, full_name: str, min_matches: int = 2) -> Tuple[bool, int, List[str]]:
        """
        Check if OFX description contains enough words from full name

        Args:
            ofx_description: OFX transaction description
            full_name: Full customer name
            min_matches: Minimum number of matching words required (default: 2)

        Returns:
            Tuple of (is_match, num_matches, matched_words)

        Examples:
            >>> match_names("Pix recebido de HEBERTON BRAVO", "HEBERTON BRAVO de Costa")
            (True, 2, ['HEBERTON', 'BRAVO'])

            >>> match_names("TED de JOAO", "JOAO SILVA SANTOS")
            (False, 1, ['JOAO'])  # Only 1 match, needs 2

            >>> match_names("PIX MARIA SANTOS OLIVEIRA", "MARIA SANTOS DE OLIVEIRA")
            (True, 3, ['MARIA', 'SANTOS', 'OLIVEIRA'])
        """
        if not ofx_description or not full_name:
            return False, 0, []

        # Extract name from OFX description
        extracted_name = NameMatcher.extract_name_from_ofx_description(ofx_description)

        # Get significant words from both
        ofx_words = NameMatcher.get_significant_words(extracted_name)
        name_words = NameMatcher.get_significant_words(full_name)

        if not ofx_words or not name_words:
            return False, 0, []

        # Find matching words
        matched_words = []
        for ofx_word in ofx_words:
            if ofx_word in name_words:
                matched_words.append(ofx_word)

        num_matches = len(matched_words)
        is_match = num_matches >= min_matches

        return is_match, num_matches, matched_words

    @staticmethod
    def find_best_name_match(ofx_description: str, candidate_names: List[str], min_matches: int = 2) -> Tuple[str, int]:
        """
        Find best matching name from a list of candidates

        Args:
            ofx_description: OFX transaction description
            candidate_names: List of possible customer names
            min_matches: Minimum number of matching words required

        Returns:
            Tuple of (best_match_name, num_matches) or (None, 0) if no match

        Example:
            >>> candidates = ["MARIA SANTOS", "JOAO SILVA", "HEBERTON BRAVO de Costa"]
            >>> find_best_name_match("Pix recebido de HEBERTON BRAVO", candidates)
            ("HEBERTON BRAVO de Costa", 2)
        """
        best_match = None
        best_score = 0

        for name in candidate_names:
            is_match, num_matches, _ = NameMatcher.match_names(ofx_description, name, min_matches)
            if is_match and num_matches > best_score:
                best_match = name
                best_score = num_matches

        return best_match, best_score
