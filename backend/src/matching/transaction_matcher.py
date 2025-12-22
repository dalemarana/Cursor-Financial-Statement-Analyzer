"""Transaction matching engine."""
from typing import List, Tuple, Optional
from datetime import date, timedelta
from decimal import Decimal
from dataclasses import dataclass
from src.models.transaction import Transaction


@dataclass
class MatchSuggestion:
    """Match suggestion data."""
    transaction1: Transaction
    transaction2: Transaction
    confidence: float
    date_difference: int
    amount_match: bool


class TransactionMatcher:
    """Matches transactions across statements."""
    
    def __init__(self, date_tolerance_days: int = 2):
        """Initialize matcher with date tolerance."""
        self.date_tolerance_days = date_tolerance_days
    
    def match_transactions(self, transactions: List[Transaction]) -> List[Tuple[Transaction, Transaction, float]]:
        """Match transactions and return list of (paid_out, paid_in, confidence) tuples."""
        paid_out = [t for t in transactions if t.transaction_type == "Paid Out"]
        paid_in = [t for t in transactions if t.transaction_type == "Paid In"]
        
        matches = []
        matched_paid_in_ids = set()
        
        for out_txn in paid_out:
            best_match = None
            best_confidence = 0.0
            
            for in_txn in paid_in:
                if in_txn.id in matched_paid_in_ids:
                    continue
                
                confidence = self._calculate_match_confidence(out_txn, in_txn)
                
                if confidence > best_confidence and confidence > 0.5:  # Minimum confidence threshold
                    best_match = in_txn
                    best_confidence = confidence
            
            if best_match:
                matches.append((out_txn, best_match, best_confidence))
                matched_paid_in_ids.add(best_match.id)
        
        return matches
    
    def _calculate_match_confidence(self, txn1: Transaction, txn2: Transaction) -> float:
        """Calculate confidence score for a potential match."""
        confidence = 0.0
        
        # Amount match (exact) - 50% weight
        if abs(float(txn1.amount) - float(txn2.amount)) < 0.01:
            confidence += 0.5
        else:
            return 0.0  # Amount must match exactly
        
        # Date match - 50% weight
        date_diff = abs((txn1.date - txn2.date).days)
        if date_diff <= self.date_tolerance_days:
            # Closer dates = higher confidence
            date_score = 1.0 - (date_diff / (self.date_tolerance_days + 1))
            confidence += 0.5 * date_score
        
        return confidence
    
    def find_potential_matches(
        self,
        transaction: Transaction,
        all_transactions: List[Transaction]
    ) -> List[MatchSuggestion]:
        """Find potential matches for an unmatched transaction."""
        suggestions = []
        
        if transaction.transaction_type == "Paid Out":
            candidates = [t for t in all_transactions if t.transaction_type == "Paid In"]
        else:
            candidates = [t for t in all_transactions if t.transaction_type == "Paid Out"]
        
        for candidate in candidates:
            # Check if amount matches
            if abs(float(transaction.amount) - float(candidate.amount)) >= 0.01:
                continue
            
            # Check date tolerance
            date_diff = abs((transaction.date - candidate.date).days)
            if date_diff > self.date_tolerance_days:
                continue
            
            confidence = self._calculate_match_confidence(transaction, candidate)
            
            if confidence > 0.5:
                suggestions.append(MatchSuggestion(
                    transaction1=transaction,
                    transaction2=candidate,
                    confidence=confidence,
                    date_difference=date_diff,
                    amount_match=True
                ))
        
        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions

