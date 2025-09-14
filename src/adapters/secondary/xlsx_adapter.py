"""XLSX operations adapter implementation."""

import logging
from typing import Any, List

from ports.xlsx import XLSXPort

logger = logging.getLogger(__name__)


class XLSXAdapter(XLSXPort):
    """PLACEHOLDER: XLSX operations implementation."""

    def read_xlsx_data(self, xlsx_path: str) -> List[Any]:
        """Read data from XLSX file.

        Args:
            xlsx_path: Path to XLSX file.

        Returns:
            List of records from XLSX.
        """
        logger.warning("PLACEHOLDER: XLSX read_xlsx_data not yet implemented")
        return []

    def append_xlsx_data(self, xlsx_path: str, data: List[Any]) -> None:
        """Append data to XLSX file.

        Args:
            xlsx_path: Path to XLSX file.
            data: Data to append.
        """
        logger.warning("PLACEHOLDER: XLSX append_xlsx_data not yet implemented")
