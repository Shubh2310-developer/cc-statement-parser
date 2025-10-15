"""Table extraction module using Camelot for transaction tables.

This module handles extraction of transaction tables from PDF credit card statements.
It supports both lattice (tables with borders) and stream (tables without borders) methods.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import camelot
import pandas as pd

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TransactionRow:
    """Represents a single transaction row."""

    date: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    credit: Optional[Decimal] = None
    debit: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    raw_data: Optional[Dict[str, Any]] = None
    row_index: Optional[int] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'description': self.description,
            'amount': float(self.amount) if self.amount else None,
            'credit': float(self.credit) if self.credit else None,
            'debit': float(self.debit) if self.debit else None,
            'balance': float(self.balance) if self.balance else None,
            'confidence': self.confidence
        }


@dataclass
class ExtractedTable:
    """Represents an extracted table."""

    page_num: int
    table_num: int
    rows: List[TransactionRow]
    headers: List[str]
    raw_df: pd.DataFrame
    confidence: float
    method: str  # 'lattice' or 'stream'

    def get_row_count(self) -> int:
        """Get number of rows."""
        return len(self.rows)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        data = [row.to_dict() for row in self.rows]
        return pd.DataFrame(data)


@dataclass
class TableExtractionResult:
    """Complete table extraction result."""

    tables: List[ExtractedTable]
    total_transactions: int
    success: bool
    error_message: Optional[str] = None


class TableExtractor:
    """Extract transaction tables from PDF documents."""

    def __init__(self):
        """Initialize table extractor."""
        self.settings = get_settings()

    def extract_tables(
        self,
        pdf_bytes: bytes,
        pages: Optional[str] = 'all',
        method: str = 'auto'
    ) -> TableExtractionResult:
        """Extract tables from PDF.

        Args:
            pdf_bytes: PDF file content as bytes
            pages: Pages to process ('all' or '1,2,3' or '1-5')
            method: Extraction method ('lattice', 'stream', or 'auto')

        Returns:
            TableExtractionResult object
        """
        logger.info(f"Extracting tables from PDF bytes (method: {method})")

        try:
            # Save bytes to temp file for camelot (camelot requires file path)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_bytes)
                tmp_path = Path(tmp_file.name)

            try:
                tables = []

                if method == 'auto':
                    # Try lattice first, then stream
                    tables_lattice = self._extract_with_method(tmp_path, pages, 'lattice')
                    tables_stream = self._extract_with_method(tmp_path, pages, 'stream')

                    # Use whichever method found more tables
                    if len(tables_lattice) >= len(tables_stream):
                        tables = tables_lattice
                    else:
                        tables = tables_stream

                else:
                    tables = self._extract_with_method(tmp_path, pages, method)
            finally:
                # Clean up temp file
                tmp_path.unlink(missing_ok=True)

            # Parse tables into transaction rows
            extracted_tables = []
            for table_info in tables:
                extracted = self._parse_table(table_info)
                if extracted:
                    extracted_tables.append(extracted)

            total_transactions = sum(t.get_row_count() for t in extracted_tables)

            logger.info(
                f"Extracted {len(extracted_tables)} tables with "
                f"{total_transactions} transactions"
            )

            return TableExtractionResult(
                tables=extracted_tables,
                total_transactions=total_transactions,
                success=True
            )

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return TableExtractionResult(
                tables=[],
                total_transactions=0,
                success=False,
                error_message=str(e)
            )

    def _extract_with_method(
        self,
        pdf_path: Path,
        pages: str,
        method: str
    ) -> List[Dict[str, Any]]:
        """Extract tables using specific method.

        Args:
            pdf_path: Path to PDF file
            pages: Pages to process
            method: 'lattice' or 'stream'

        Returns:
            List of table information dicts
        """
        try:
            if method == 'lattice':
                # Lattice method - for tables with borders
                tables = camelot.read_pdf(
                    str(pdf_path),
                    pages=pages,
                    flavor='lattice',
                    strip_text='\n',
                    line_scale=40
                )
            else:
                # Stream method - for tables without borders
                tables = camelot.read_pdf(
                    str(pdf_path),
                    pages=pages,
                    flavor='stream',
                    strip_text='\n',
                    edge_tol=50,
                    row_tol=10,
                    column_tol=10
                )

            logger.info(f"Found {len(tables)} tables with {method} method")

            result = []
            for i, table in enumerate(tables):
                result.append({
                    'table': table,
                    'df': table.df,
                    'page': table.page,
                    'accuracy': table.accuracy if hasattr(table, 'accuracy') else 0.0,
                    'method': method,
                    'table_num': i
                })

            return result

        except Exception as e:
            logger.warning(f"Table extraction with {method} failed: {e}")
            return []

    def _parse_table(self, table_info: Dict[str, Any]) -> Optional[ExtractedTable]:
        """Parse extracted table into structured data.

        Args:
            table_info: Table information dict

        Returns:
            ExtractedTable object or None if parsing fails
        """
        try:
            df = table_info['df']
            page = table_info['page']
            method = table_info['method']
            table_num = table_info['table_num']
            accuracy = table_info['accuracy']

            if df.empty:
                return None

            # Clean the dataframe
            df = self._clean_dataframe(df)

            # Detect headers
            headers = self._detect_headers(df)

            # Identify column types
            col_mapping = self._identify_columns(headers)

            if not col_mapping:
                logger.warning(f"Could not identify columns in table {table_num}")
                return None

            # Parse rows
            rows = []
            for idx, row in df.iterrows():
                if idx == 0 and self._is_header_row(row):
                    continue  # Skip header row

                transaction = self._parse_row(row, col_mapping)
                if transaction and transaction.description:  # Valid transaction
                    transaction.row_index = idx
                    rows.append(transaction)

            if not rows:
                return None

            extracted_table = ExtractedTable(
                page_num=page,
                table_num=table_num,
                rows=rows,
                headers=headers,
                raw_df=df,
                confidence=accuracy / 100.0 if accuracy else 0.5,
                method=method
            )

            logger.info(
                f"Parsed table {table_num} on page {page}: "
                f"{len(rows)} transactions"
            )

            return extracted_table

        except Exception as e:
            logger.error(f"Failed to parse table: {e}")
            return None

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize dataframe.

        Args:
            df: Raw dataframe

        Returns:
            Cleaned dataframe
        """
        # Strip whitespace from all cells
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Remove completely empty rows
        df = df.replace('', pd.NA).dropna(how='all')

        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')

        # Reset index
        df = df.reset_index(drop=True)

        return df

    def _detect_headers(self, df: pd.DataFrame) -> List[str]:
        """Detect table headers.

        Args:
            df: DataFrame

        Returns:
            List of header names
        """
        headers = []

        # Check if first row looks like a header
        if len(df) > 0:
            first_row = df.iloc[0]

            # If first row has header-like text, use it
            if self._is_header_row(first_row):
                headers = [str(val).strip() for val in first_row.values]
            else:
                # Use column indices as headers
                headers = [f"col_{i}" for i in range(len(df.columns))]
        else:
            headers = [f"col_{i}" for i in range(len(df.columns))]

        return headers

    def _is_header_row(self, row: pd.Series) -> bool:
        """Check if row looks like a header.

        Args:
            row: DataFrame row

        Returns:
            True if row appears to be a header
        """
        # Convert to strings
        values = [str(v).strip().lower() for v in row.values]

        # Header keywords
        header_keywords = [
            'date', 'description', 'amount', 'credit', 'debit',
            'balance', 'transaction', 'details', 'particular',
            'posting', 'reference', 'type', 'category'
        ]

        # Check if any value contains header keywords
        for value in values:
            if any(keyword in value for keyword in header_keywords):
                return True

        return False

    def _identify_columns(self, headers: List[str]) -> Dict[str, int]:
        """Identify which column contains which type of data.

        Args:
            headers: List of header names

        Returns:
            Mapping of field names to column indices
        """
        mapping = {}

        for i, header in enumerate(headers):
            header_lower = header.lower()

            # Date column
            if any(kw in header_lower for kw in ['date', 'posting', 'trans date']):
                if 'date' not in mapping:
                    mapping['date'] = i

            # Description column
            elif any(kw in header_lower for kw in ['description', 'particular', 'details', 'transaction', 'merchant']):
                if 'description' not in mapping:
                    mapping['description'] = i

            # Amount column
            elif 'amount' in header_lower:
                if 'amount' not in mapping:
                    mapping['amount'] = i

            # Credit column
            elif 'credit' in header_lower or 'cr' in header_lower:
                if 'credit' not in mapping:
                    mapping['credit'] = i

            # Debit column
            elif 'debit' in header_lower or 'dr' in header_lower:
                if 'debit' not in mapping:
                    mapping['debit'] = i

            # Balance column
            elif 'balance' in header_lower:
                if 'balance' not in mapping:
                    mapping['balance'] = i

        return mapping

    def _parse_row(
        self,
        row: pd.Series,
        col_mapping: Dict[str, int]
    ) -> Optional[TransactionRow]:
        """Parse a single table row into a transaction.

        Args:
            row: DataFrame row
            col_mapping: Column mapping

        Returns:
            TransactionRow object or None
        """
        try:
            transaction = TransactionRow()

            # Extract date
            if 'date' in col_mapping:
                date_str = str(row.iloc[col_mapping['date']]).strip()
                if date_str and date_str != 'nan':
                    transaction.date = date_str

            # Extract description
            if 'description' in col_mapping:
                desc = str(row.iloc[col_mapping['description']]).strip()
                if desc and desc != 'nan':
                    transaction.description = desc

            # Extract amounts
            if 'amount' in col_mapping:
                amount_str = str(row.iloc[col_mapping['amount']]).strip()
                transaction.amount = self._parse_amount(amount_str)

            if 'credit' in col_mapping:
                credit_str = str(row.iloc[col_mapping['credit']]).strip()
                transaction.credit = self._parse_amount(credit_str)

            if 'debit' in col_mapping:
                debit_str = str(row.iloc[col_mapping['debit']]).strip()
                transaction.debit = self._parse_amount(debit_str)

            if 'balance' in col_mapping:
                balance_str = str(row.iloc[col_mapping['balance']]).strip()
                transaction.balance = self._parse_amount(balance_str)

            # Calculate confidence based on completeness
            filled_fields = sum([
                bool(transaction.date),
                bool(transaction.description),
                bool(transaction.amount or transaction.credit or transaction.debit)
            ])
            transaction.confidence = filled_fields / 3.0

            return transaction

        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def _parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal.

        Args:
            amount_str: Amount string

        Returns:
            Decimal amount or None
        """
        if not amount_str or amount_str == 'nan':
            return None

        try:
            # Remove currency symbols and commas
            cleaned = amount_str.replace('\u20b9', '').replace('Rs', '').replace('$', '').replace(',', '').strip()

            # Handle negative amounts
            is_negative = False
            if '(' in cleaned and ')' in cleaned:
                is_negative = True
                cleaned = cleaned.replace('(', '').replace(')', '')
            elif cleaned.startswith('-'):
                is_negative = True
                cleaned = cleaned[1:]

            # Parse to Decimal
            amount = Decimal(cleaned)

            if is_negative:
                amount = -amount

            return amount

        except Exception as e:
            logger.debug(f"Could not parse amount '{amount_str}': {e}")
            return None

    def extract_table_from_region(
        self,
        pdf_path: Path,
        page: int,
        table_areas: List[str],
        method: str = 'lattice'
    ) -> Optional[ExtractedTable]:
        """Extract table from specific region on page.

        Args:
            pdf_path: Path to PDF file
            page: Page number (1-indexed)
            table_areas: List of table area coordinates ['x1,y1,x2,y2']
            method: Extraction method

        Returns:
            ExtractedTable object or None
        """
        try:
            tables = camelot.read_pdf(
                str(pdf_path),
                pages=str(page),
                flavor=method,
                table_areas=table_areas
            )

            if not tables:
                return None

            table_info = {
                'table': tables[0],
                'df': tables[0].df,
                'page': page,
                'accuracy': tables[0].accuracy if hasattr(tables[0], 'accuracy') else 0.0,
                'method': method,
                'table_num': 0
            }

            return self._parse_table(table_info)

        except Exception as e:
            logger.error(f"Failed to extract table from region: {e}")
            return None
