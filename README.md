## Now supports most of the mermaid diagram genration using deepseek (provided by groq)

### Examples :
![Screenshot 2025-06-05 235406](https://github.com/user-attachments/assets/5a8572f6-1028-4db6-9a89-a1f9715e8c31)

![Screenshot 2025-06-06 000507](https://github.com/user-attachments/assets/190a392f-9fc3-4d4b-ba5e-118688854c54)

![Screenshot 2025-06-06 000538](https://github.com/user-attachments/assets/c489f8fb-cb60-48cb-ad1a-4b0ab317cfad)

![Screenshot 2025-06-06 000709](https://github.com/user-attachments/assets/5208f5f2-98cb-4b09-b508-bde6aea4f386)

![Screenshot 2025-06-06 000819](https://github.com/user-attachments/assets/b6134f21-eb87-45ee-a446-d6b8142da311)



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
