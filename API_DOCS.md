# API Documentation

Base URL path is `/api`. All endpoints aside from `/auth/signup` and `/auth/login` require an active Bearer Token injected into the HTTP Header (`Authorization: Bearer <TOKEN>`).

## Authentication Module (`/auth`)

### `POST /auth/signup`
Creates a brand new user.
*   **Body (JSON)**: `{"email": "user@example.com", "password": "mypassword"}`
*   **Response (201)**: Returns the newly created User Object with its numerical ID.

### `POST /auth/login`
Validates credentials and hands back relatively short-lived JWTs (defaults to 7 days access bounds). Uses OAuth2 Form specifications.
*   **Body (Form Data)**: `username=user@example.com&password=mypassword`
*   **Response (200)**: `{"access_token": "eyJhb...", "token_type": "bearer"}`

---

## Workspace Module (`/workspaces`)

### `GET /workspaces`
Retrieves all workspaces securely tied to the currently signed in user instance.
*   **Response (200)**: A list of workspace objects.

### `POST /workspaces`
Initializes a new workspace.
*   **Body (JSON)**: `{"name": "My AI Project"}`
*   **Response (201)**: The newly created workspace object containing empty Excalidraw and Editor.js fields.

### `GET /workspaces/{id}`
Returns details for a singular targeted workspace scope. Ensure user validation ownership per scope prior to resolving state data.

### `PUT /workspaces/{id}`
General update block. Ideal for persisting frontend UI state architectures (like raw Excalidraw outputs or nested JSON structure arrays for Editor.js).
*   **Body (JSON)**: `{"name": "New Name", "excalidraw_data": {"elements": [...]}, "editorjs_data": {"blocks": [...]}}`
*   **Response (200)**: The updated target workspace.

### `DELETE /workspaces/{id}`
Trunks a workspace from active index. Requires ownership validation validation. (204 No Content).

---

## Document Integration Module (`/workspaces`)
Documents actively integrate towards Vector mapping algorithms designed asynchronously against PGVector datalinks.

### `POST /workspaces/{id}/documents`
Takes either an active `.pdf` stream or `.txt` buffer block for server ingestion. Immediately triggers an NLP embedding queue targeting workspace indexing limits using LangChain loaders and Recursive Splitter models via Gemini/Groq instances. Must pass as multipart form data.
*   **Body (Multipart Form)**: `file`
*   **Response (200)**: An internal structural tag representing document ID mapping indices against target workspace scopes. 

### `GET /workspaces/{id}/documents`
Provides an active structural list regarding all attached source document maps active for global analysis.

---

## Global Inference Layer (`/chat`)

All routes within the chat layer utilize centrally managed LLM models integrated into LangChain workflows within `app/services/ai_service.py`.

### `POST /chat/generate`
Specific route taking in generalized textual requests and forcefully returning Mermaid diagram architecture JSON mappings. Use this to translate concept descriptions directly to renderable frontend visualizations.
*   **Body**: `{"prompt": "Create a mind map of renewable energy sources"}`
*   **Response**: `{"result": "mindmap\n  root((Energy))\n    Solar\n    Wind..."}`

### `POST /chat/ask`
A conversational query interface applying active RAG contexts mapping back to source uploaded workspace files.
*   **Body**: `{"question": "What is the key conclusion from the uploaded Q3 report?", "workspace_id": 5}`
*   **Response**: `{"result": "Based on the provided documents..."}`

### `POST /chat/general`
Multipurpose gateway handling all other UI tasks including general LLM inference questions or complex math diagram evaluation logic provided from UI components like Excalidraw. Accepts generalized strings or base64 rendered PNG layers bridging multi-model Vision analysis flows.
*   **Body (JSON)**: `{"prompt": "Optional prompt", "image_base64": "data:image/png;base64,iVB...", "dict_of_vars": {}}`
*   **Response**: `{"result": [...]}` / `{"result": "Textual answer"}`
