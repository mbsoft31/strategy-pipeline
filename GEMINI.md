## Project Overview

This project, "Strategy Pipeline," is a powerful tool designed to assist researchers in creating robust and reproducible search strategies for academic databases. It combines the power of Large Language Models (LLMs) with a deterministic query-building engine to generate syntactically correct queries for multiple databases, effectively preventing LLM "hallucinations" of incorrect query syntax.

The project is architected with a Python backend and a modern web frontend.

**Backend:**

*   **Framework:** The backend is built using a combination of Flask for the main web application and Streamlit for a demonstrative UI.
*   **Core Logic:** The core of the application is the `PipelineController` (`src/controller.py`), which orchestrates the research pipeline through a series of stages. These stages include:
    1.  **Project Setup:** Defining the initial research idea.
    2.  **Problem Framing:** Structuring the problem and identifying key concepts.
    3.  **Research Questions:** Generating relevant research questions.
    4.  **Search Concept Expansion:** Expanding on the initial concepts.
    5.  **Database Query Plan:** Generating the final, syntactically correct queries for various databases.
*   **LLM Integration:** The application integrates with LLMs through a `ModelService`, with support for providers like OpenAI and OpenRouter.
*   **Anti-Hallucination:** A key feature is the "Anti-Hallucination Query Engine," which uses a deterministic approach to build queries, ensuring they are valid for the target database.
*   **Persistence:** The application uses a `PersistenceService` to save and load project artifacts, allowing for a complete audit trail of the research process.

**Frontend:**

*   **Framework:** The main frontend is a single-page application built with React and Vite.
*   **Language:** The frontend is written in TypeScript, ensuring type safety and improved developer experience.
*   **Styling:** The UI is styled with Tailwind CSS, providing a modern and responsive design.
*   **Key Libraries:** The frontend utilizes several popular libraries from the TanStack ecosystem, including:
    *   **TanStack Router:** For client-side routing.
    *   **TanStack Query:** For managing server state and data fetching.
    *   **TanStack Table:** For displaying tabular data.

**Demonstrative UI:**

The project also includes a Streamlit application (`app.py`) that provides a visual and interactive way to step through the research pipeline. This serves as a great tool for understanding the workflow and the capabilities of the system.

## Building and Running

### Backend

1.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```
2.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure LLM provider:**
    *   Copy the example environment file:
        ```bash
        copy .env.example .env
        ```
    *   Edit the `.env` file to configure your desired LLM provider (e.g., `openai`, `openrouter`, or `mock`).
5.  **Run the Flask application:**
    ```bash
    flask run
    ```
    The application will be available at `http://127.0.0.1:5000`.

### Frontend

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend/strategy-pipeline-ui
    ```
2.  **Install dependencies:**
    ```bash
    npm install
    ```
3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:3000`.

### Streamlit UI

1.  **Ensure backend dependencies are installed.**
2.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    The Streamlit UI will be available at `http://localhost:8501`.

## Testing

The project includes a suite of tests to ensure the quality and correctness of the code.

*   **Run all tests:**
    ```bash
    pytest
    ```
*   **Run a specific test file:**
    ```bash
    pytest tests/test_stage_workflow.py
    ```

## Development Conventions

The project follows a set of conventions to maintain code quality and consistency.

*   **Backend:**
    *   The backend code is organized into modules within the `src` directory, following a clear separation of concerns (e.g., `services`, `stages`, `models`).
    *   Pydantic is used for data modeling and validation, ensuring that data structures are well-defined and consistent.
*   **Frontend:**
    *   The frontend code is organized using a feature-based structure, with components, routes, and hooks grouped by functionality.
    *   The project uses Prettier for code formatting and ESLint for linting, ensuring a consistent code style.
*   **Commits:** The project encourages the use of Conventional Commits for clear and descriptive commit messages.
