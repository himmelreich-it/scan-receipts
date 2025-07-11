"""Final summary display for file processing completion."""


class SummaryDisplay:
    """Displays comprehensive summary at completion of file processing."""

    def __init__(self) -> None:
        """Initialize summary display with zero counters."""
        self.processed_count = 0
        self.error_count = 0
        self.duplicate_count = 0

    def set_counters(self, processed: int, errors: int, duplicates: int) -> None:
        """Set the processing counters for summary display.

        Args:
            processed: Number of files processed successfully
            errors: Number of errors encountered
            duplicates: Number of duplicates skipped
        """
        self.processed_count = processed
        self.error_count = errors
        self.duplicate_count = duplicates

    def display_summary(self) -> None:
        """Display comprehensive summary of processing results.

        Shows total files processed successfully, count of errors encountered,
        and count of duplicates skipped after all processing completes.
        """
        print()  # Empty line for visual separation
        print("=== PROCESSING SUMMARY ===")
        print(f"Files processed successfully: {self.processed_count}")
        print(f"Errors encountered: {self.error_count}")
        print(f"Duplicates skipped: {self.duplicate_count}")

        # Calculate and display total files attempted
        total_attempted = self.processed_count + self.error_count + self.duplicate_count
        print(f"Total files attempted: {total_attempted}")

        # Display completion message
        if self.error_count == 0:
            print("Processing completed successfully!")
        else:
            print(f"Processing completed with {self.error_count} error(s).")

    def get_total_attempted(self) -> int:
        """Get the total number of files that were attempted to be processed.

        Returns:
            Total count of files attempted (processed + errors + duplicates)
        """
        return self.processed_count + self.error_count + self.duplicate_count

    def get_success_rate(self) -> float:
        """Get the success rate as a percentage.

        Returns:
            Success rate as a float between 0.0 and 100.0
            Returns 0.0 if no files were attempted
        """
        total = self.get_total_attempted()
        if total == 0:
            return 0.0
        return (self.processed_count / total) * 100.0

    def reset_counters(self) -> None:
        """Reset all counters to zero.

        Useful for starting a new processing session.
        """
        self.processed_count = 0
        self.error_count = 0
        self.duplicate_count = 0
