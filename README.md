## How Data Flows with Models

Let's revisit the flow from Chapter 1, now including the data model validation steps:

```mermaid
sequenceDiagram
    participant Frontend Browser
    participant FastAPI App
    participant Pydantic (Validation)
    participant generate_mermaid function
    participant LLM Chain (Internal Logic)

    Frontend Browser->>FastAPI App: POST /generate-mermaid request (JSON: {"prompt": "make a flowchart"})
    FastAPI App->>FastAPI App: Receives request
    FastAPI App->>FastAPI App: Looks up route (@app.post("/generate-mermaid"))
    FastAPI App->>Pydantic (Validation): Validate incoming JSON against DiagramRequest
    alt Validation Successful
        Pydantic (Validation)-->>FastAPI App: Validated data (as DiagramRequest object)
        FastAPI App->>generate_mermaid function: Calls generate_mermaid(data=DiagramRequest object)
        generate_mermaid function->>LLM Chain (Internal Logic): Processes prompt
        LLM Chain (Internal Logic)-->>generate_mermaid function: Returns result (e.g., {"mermaid_syntax": "..."})
        generate_mermaid function-->>FastAPI App: Returns DiagramResponse object
        FastAPI App->>Pydantic (Validation): Validate returned object against DiagramResponse
        Pydantic (Validation)-->>FastAPI App: Validated/Formatted JSON response
        FastAPI App->>Frontend Browser: Sends JSON response ({"mermaid_syntax": "..."})
    else Validation Failed
        Pydantic (Validation)-->>FastAPI App: Validation Error
        FastAPI App-->>Frontend Browser: Sends Error Response (e.g., 422 Unprocessable Entity)
    end
```

As you can see, Pydantic validation happens automatically thanks to FastAPI integrating with it. This ensures only correctly formatted data makes it to your core logic and that your responses follow a defined structure.

## Other Data Models in Our Project

Our project uses other models for different types of requests:

| Model Name       | Used In Endpoint   | Purpose                                       | Structure Expectation                                   |
| :--------------- | :----------------- | :-------------------------------------------- | :------------------------------------------------------ |
| `QuestionData`   | `/ask-ai`          | Receiving a text question from the frontend.  | Expects a field `question` which is a string.           |
| `ImageData`      | `/calculate`       | Receiving an image (as base64) and variables. | Expects a field `image` (string, base64 data) and `dict_of_vars` (a dictionary). |
| `AnswerData`     | `/ask-ai`          | Sending back the AI's text answer.            | Expects a field `result` which is a string.             |
