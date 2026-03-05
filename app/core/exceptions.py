from typing import Any, Dict, Optional

class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        detail: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(detail)
        self.status_code = status_code
        self.error_code = error_code
        self.detail = detail
        self.context = context or {}

class AIAnalysisError(AppException):
    """Raised when AI fails to analyse or generate correctly."""
    def __init__(self, detail: str = "AI analysis failed"):
        super().__init__(
            status_code=500,
            error_code="AI_ANALYSIS_ERROR",
            detail=detail
        )

class UnsupportedFileTypeError(AppException):
    """Raised when an uploaded file is not supported."""
    def __init__(self, detail: str = "Unsupported file type"):
        super().__init__(
            status_code=400,
            error_code="UNSUPPORTED_FILE",
            detail=detail
        )

class DocumentProcessingError(AppException):
    """Raised when document ingestion or retrieval fails."""
    def __init__(self, detail: str = "Document processing failed"):
        super().__init__(
            status_code=500,
            error_code="DOCUMENT_PROCESSING_ERROR",
            detail=detail
        )

class WorkspaceNotFoundError(AppException):
    """Raised when a workspace is not found or user lacks access."""
    def __init__(self, detail: str = "Workspace not found"):
        super().__init__(
            status_code=404,
            error_code="WORKSPACE_NOT_FOUND",
            detail=detail
        )
