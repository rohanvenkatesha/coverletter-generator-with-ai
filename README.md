# Cover Letter Generator

This is a full-stack application that helps you generate professional cover letters. You can either provide your own custom content or leverage AI to generate a tailored cover letter based on your resume and a job description.

---

## Features

* **AI-Powered Generation:** Upload your resume (PDF) and paste a job description to get an AI-generated cover letter.
* **Custom Content:** Write your own cover letter content and generate it into a professional PDF.
* **Personalized Details:** Easily include your contact information and target employer/job title.
* **PDF Output:** Generates a downloadable PDF file of your cover letter.

---

## Technologies Used

* **Frontend:** React, TypeScript, Axios, Tailwind CSS (for styling)
* **Backend:** FastAPI, Python, PyPDF2, OpenAI API, WeasyPrint, Jinja2

---

## Setup Instructions

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

Before you start, make sure you have the following installed:

* **Node.js & npm/Yarn:** For the React frontend.
* **Python 3.8+ & pip:** For the FastAPI backend.
* **OpenAI API Key:** Required for the AI generation feature. You can get one from the [OpenAI website](https://platform.openai.com/account/api-keys).
* **Git:** For cloning the repository (if you haven't already).

---

### 2. WeasyPrint System Dependencies (Crucial for PDF Generation)

**WeasyPrint** (used in the backend to convert HTML to PDF) requires specific system libraries. Without these, PDF generation will fail.

#### For Windows Users (Important!)

WeasyPrint relies on GTK. The most reliable way to get this working is to install the **GTK3 runtime for Windows**.

1.  **Download and Install GTK3 Runtime:**
    Locate and run the setup file for **`gtk3-runtime-3.24.24-2021-01-30-ts-win64`** (or a similar, more recent stable version if available). This installer typically includes essential DLLs like `cairo.dll`, `pango.dll`, `gdk-pixbuf.dll`, and **`gobject-2.0-0.dll`**, which WeasyPrint needs.
2.  **Follow the Installation Prompts:** During the installation, it's **crucial to select the option to add GTK to your system's `PATH` environment variable**. This ensures your Python environment can find these necessary DLLs.
3.  **Verify Installation and PATH:**
    After installation, open your system's Environment Variables (search "Environment Variables" in the Windows Start Menu). Under "System variables," find the `Path` variable and click "Edit." Confirm that an entry pointing to the `bin` directory of your GTK installation (e.g., `C:\Program Files\GTK3-Runtime\bin` or similar) is present.
4.  **Restart Your Terminal:**
    After installing GTK and modifying environment variables, **close all existing terminal/command prompt windows and open new ones** to ensure the new `PATH` settings are loaded.

**Recommended Alternatives for Windows:** If you encounter persistent issues, consider using:
* **Windows Subsystem for Linux (WSL):** Install a Linux distribution (like Ubuntu) via WSL and set up your Python backend environment there. This simplifies WeasyPrint dependencies significantly.
* **Docker:** Run your FastAPI backend in a Docker container, where the Linux dependencies can be easily managed.

#### For Linux (Debian/Ubuntu-based):

```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libpango1.0-0 libcairo2 libgdk-pixbuf2.0-0
```

#### For macOS (using Homebrew):

```bash
brew install libxml2 libxslt libffi cairo pango gdk-pixbuf
brew install pygobject3 # For GObject introspection bindings
```

---

### 3. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd path/to/your/backend-folder # e.g., cd cover-letter-generator/backend
    ```
2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    * **Windows:** `.\venv\Scripts\activate`
    * **Linux/macOS:** `source venv/bin/activate`
4.  **Install Python dependencies:**
    Create a `requirements.txt` file in your backend directory with the following content:
    ```
    fastapi==0.111.0
    uvicorn==0.30.1
    python-multipart==0.0.9
    PyPDF2==3.0.1
    openai==1.35.13
    weasyprint==62.0
    Jinja2==3.1.4
    ```
    Then install them using:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Set your OpenAI API key:**
    * **Windows (Command Prompt):** `set OPENAI_API_KEY="your_api_key_here"`
    * **Windows (PowerShell):** `$env:OPENAI_API_KEY="your_api_key_here"`
    * **Linux/macOS (Bash/Zsh):** `export OPENAI_API_KEY="your_api_key_here"`
    Replace `"your_api_key_here"` with your actual API key.
6.  **Ensure you have the Jinja2 template:**
    Make sure you have a `templates` folder in your backend directory, and inside it, a file named `cover_letter.html` with your cover letter HTML structure.
7.  **Run the FastAPI backend:**
    ```bash
    python main.py
    # Or more robustly for development (with auto-reload):
    # uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend should now be running on `http://localhost:8000`. Keep this terminal window open.

---

### 4. Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd path/to/your/frontend-folder # e.g., cd cover-letter-generator/frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    # or yarn install
    ```
3.  **Run the React frontend:**
    ```bash
    npm start
    # or yarn start
    ```
    The frontend should open in your browser, typically at `http://localhost:3000`.

---

## Usage

1.  Open your web browser and navigate to `http://localhost:3000`.
2.  Fill in your personal information, employer details, and job title.
3.  **Choose your cover letter generation method:**
    * **"Use AI to Generate Cover Letter" (checkbox checked):** Upload your resume PDF and paste the full job description into the provided text area.
    * **Custom Content:** Keep the checkbox unchecked and paste your own pre-written cover letter content into the text area.
4.  Click the "**Generate Cover Letter**" button.
5.  A PDF file named `cover_letter.pdf` will be automatically downloaded to your computer.

---

## Customizing the Cover Letter Template

The PDF cover letter is generated from an HTML template located at `backend/templates/cover_letter.html`. You can customize the look and feel of your cover letter by editing this HTML file and its embedded CSS.

When customizing, it's crucial to use the correct **Jinja2 placeholders** to ensure your dynamic data from the form is inserted correctly. Here are the available placeholders:

| Placeholder Variable | Description                                    | Example Usage in HTML                |
| :------------------- | :--------------------------------------------- | :----------------------------------- |
| `{{ name }}`         | Your full name (e.g., "John Doe")              | `<p>{{ name }}</p>`                 |
| `{{ email }}`        | Your email address                             | `<p>{{ email }}</p>`                |
| `{{ phone }}`        | Your phone number                              | `<p>{{ phone }}</p>`                |
| `{{ linkedin }}`     | Your LinkedIn profile URL (optional)           | `<p><a href="{{ linkedin }}">LinkedIn</a></p>` |
| `{{ github }}`       | Your GitHub profile URL (optional)             | `<p><a href="{{ github }}">GitHub</a></p>` |
| `{{ portfolio }}`    | Your Portfolio URL (optional)                  | `<p><a href="{{ portfolio }}">Portfolio</a></p>` |
| `{{ employer }}`     | The name of the employer you're applying to    | `<p>{{ employer }}</p>`             |
| `{{ job_title }}`    | The job title you're applying for              | `<p>{{ job_title }}</p>`            |
| `{{ current_date }}` | The current date (e.g., "June 14, 2025")       | `<p>{{ current_date }}</p>`         |
| `{% for paragraph in body_paragraphs %}`...`{% endfor %}` | A loop that iterates over each paragraph of the cover letter body text (generated by AI or custom). You should wrap `{{ paragraph | e }}` inside a paragraph tag. | `<p>{{ paragraph | e }}</p>`        |

**Important Notes for Customization:**

* **Jinja2 Syntax:** Placeholders are enclosed in double curly braces `{{ variable_name }}`. Logic constructs (like loops) are in `{% ... %}`.
* **Escaping Content (`| e`):** For user-provided content like the `body_paragraphs`, it's good practice to use `{{ paragraph | e }}`. The `| e` (or `| escape`) filter escapes any HTML special characters, preventing cross-site scripting (XSS) vulnerabilities if malicious HTML were accidentally included in the input.
* **CSS Styling:** All styling should be embedded directly within `<style>` tags in the HTML file, as external CSS files are not always reliably picked up by `weasyprint` for PDF conversion.

---

## Troubleshooting

* **"AxiosError: Network Error" / "Something Went Wrong" (Frontend)**:
    * **Is the backend running?** Ensure you have `python main.py` or `uvicorn` running in a *separate* terminal. If that terminal was closed, restart the backend.
    * **Is the backend accessible?** In your browser, try navigating directly to `http://localhost:8000/test-pdf`. If this doesn't load or gives a connection error, your backend isn't running or isn't accessible. Check the backend terminal for specific error messages.
    * **Firewall:** Temporarily disable your firewall to see if it's blocking the connection between frontend and backend.
    * **Port in use:** If you see "Address already in use" when starting the backend, another program is using port 8000. Stop the other program or change the port in both frontend and backend code.
* **PDF Generation Fails (Backend Errors)**:
    * **WeasyPrint Dependencies:** If the backend runs but PDF generation fails, check the backend terminal for errors related to WeasyPrint (e.g., missing DLLs, `cairo`, `pango`). Carefully review the "WeasyPrint System Dependencies" section and ensure all steps, especially for Windows, have been completed and your terminal restarted.
    * **OpenAI API Key Errors**: If AI generation fails, ensure your `OPENAI_API_KEY` environment variable is correctly set in the terminal *before* you launch the backend.
    * **PDF Extraction Issues**: If your resume PDF causes errors, try a simpler PDF or ensure it's not encrypted or corrupted.
* **Custom Template Issues**: If your custom `cover_letter.html` isn't rendering correctly in the PDF, check for:
    * Typos in placeholder names (e.g., `{{ name }}` vs `{{ Name }}`).
    * Incorrect Jinja2 syntax (e.g., `{% for ... %}` vs `{{ for ... }}`).
    * External CSS links; all CSS should be embedded in `<style>` tags.
