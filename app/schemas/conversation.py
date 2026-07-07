from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """A single message entry in a conversation log."""
    role: str = Field(..., description="Role of the sender: 'user' or 'assistant'.")
    content: str = Field(..., description="Text content of the message.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Message timestamp.")


class ConversationMetadata(BaseModel):
    """Audit and statistics metadata for a conversation."""
    conversation_id: str = Field(..., description="Conversation UUID.")
    dataset_id: str = Field(..., description="Profiled dataset UUID.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Conversation start timestamp.")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last message timestamp.")
    message_count: int = Field(0, description="Total number of messages in history.")


class Conversation(BaseModel):
    """Unified state container for a stateful conversation."""
    conversation_id: str = Field(..., description="Conversation UUID.")
    dataset_id: str = Field(..., description="Dataset UUID.")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Historical messages.")
    metadata: ConversationMetadata = Field(..., description="Conversation metadata.")


class UserQuestion(BaseModel):
    """Request payload containing user query and stateful session ID."""
    query: str = Field(..., description="Natural language analytical question.")
    conversation_id: Optional[str] = Field(None, description="Active session ID. If null, a new session is generated.")


class IntentRequest(BaseModel):
    """Payload package matching requirements for intent routing requests."""
    query: str = Field(..., description="Active question.")
    conversation_history: List[ConversationMessage] = Field(default_factory=list, description="List of previous turns.")


class IntentResponse(BaseModel):
    """
    Structured query parameters parsed from a natural language request,
    matching enterprise BI copilot capabilities.
    """
    action: str = Field(..., description="Action: FILTER, GROUP, SORT, LIMIT, COMPARE, TREND, CORRELATION, DISTRIBUTION, TIME_SERIES, TOP_K, BOTTOM_K, PERCENTAGE, AVERAGE, MEDIAN, COUNT, SUM, MIN, MAX, DISTINCT_COUNT, DRILL_DOWN, ROLLUP, GENERAL_EXPLANATION, UNKNOWN.")
    filters: List[Dict[str, Any]] = Field(default_factory=list, description="Array of filters: [{'column': 'col', 'operator': 'greater_than'|'equals', 'value': 60}].")
    group_by: Optional[str] = Field(None, description="Column key to group results by.")
    aggregation: Optional[str] = Field(None, description="Metric operation (count, sum, average, median, min, max).")
    sort: Optional[str] = Field("descending", description="Sort order: 'descending', 'ascending'.")
    limit: Optional[int] = Field(None, description="Limit count.")
    visualization: Optional[str] = Field(None, description="Suggested chart: 'bar', 'pie', 'line', 'boxplot', 'heatmap', 'card', 'table'.")
    kpi_name: Optional[str] = Field(None, description="Matching planned KPI name.")
    explanation_request: Optional[str] = Field(None, description="Open-ended explanation question.")


class QueryResult(BaseModel):
    """Structured analytical outcomes computed from DataFrames."""
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Data rows.")
    summary: str = Field(..., description="Simple text summary description.")
    columns: List[str] = Field(default_factory=list, description="List of output columns.")


class IntentExecution(BaseModel):
    """Summary of intent processing runtime statistics."""
    intent: IntentResponse = Field(..., description="Executed intent.")
    query_result: QueryResult = Field(..., description="Deterministic outcomes.")
    execution_time_ms: float = Field(0.0, description="Duration in ms.")
    success: bool = Field(True, description="Success flag.")
    error_message: Optional[str] = Field(None, description="Error logs if failed.")


class ConversationalChatResponse(BaseModel):
    """Unified API payload returned to frontends for chat rendering."""
    conversation_id: str = Field(..., description="Session ID.")
    intent: IntentResponse = Field(..., description="Parsed structured intent JSON.")
    execution_result: QueryResult = Field(..., description="Deterministic query results.")
    formatted_response: Dict[str, Any] = Field(..., description="Formatted output (tables, metric cards, charts).")
    suggested_visualization: Optional[str] = Field(None, description="Visual recommendation type.")
    nl_explanation: str = Field(..., description="Narrative summary explanation.")
    metadata: ConversationMetadata = Field(..., description="Updated metadata.")
