from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import Optional
import io
import os
import weasyprint
import openai
import PyPDF2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS from your frontend (adjust if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Load OpenAI API Key from environment variable
# It's crucial to set this before running the application:
# export OPENAI_API_KEY="your_api_key_here" (Linux/macOS)
# set OPENAI_API_KEY=your_api_key_here (Windows CMD)
# $env:OPENAI_API_KEY="your_api_key_here" (Windows PowerShell)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.warning("OPENAI_API_KEY environment variable not set. AI generation will not work.")


async def extract_text_from_pdf(file: UploadFile) -> str:
    """Extracts text content from a PDF file."""
    try:
        contents = await file.read()
        reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            # PyPDF2's extract_text can return None for empty pages
            text += (page.extract_text() or "") + "\n"
        return text
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Error reading PDF: {e}")
        raise HTTPException(status_code=400, detail=f"Could not read resume PDF: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during PDF text extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing resume PDF: {e}")


async def generate_ai_cover_letter(resume_text: str, job_description: str) -> str:
    """Generates a cover letter using OpenAI's GPT model."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured on the server.")

    prompt = (
        f"Write a professional, tailored cover letter based on this resume and job description.\n\n"
        f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}\n\n"
        f"Please write the cover letter in a polite and professional tone. "
        f"Focus on highlighting relevant skills and experiences from the resume that match the job description. "
        f"Keep it concise, typically 3-4 paragraphs."
    )
    try:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for writing cover letters. Your goal is to write a compelling and concise cover letter."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=700, # Increased max_tokens slightly for longer letters if needed
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during AI generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI cover letter: {e}")


@app.post("/generate")
async def generate_cover_letter(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    linkedin: Optional[str] = Form(None),
    github: Optional[str] = Form(None),
    portfolio: Optional[str] = Form(None),
    employer: str = Form(...),  # <-- ADDED THIS
    job_title: str = Form(...), # <-- ADDED THIS
    job_description: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    custom_content: Optional[str] = Form(None),
    use_ai: str = Form(False), # Frontend sends boolean as string, so receive as string
):
    try:
        # Convert use_ai string to boolean
        use_ai_bool = use_ai.lower() == 'true'

        body_text = ""
        if use_ai_bool:
            if not resume:
                raise HTTPException(status_code=400, detail="Resume PDF is required when using AI generation.")
            if not job_description or not job_description.strip():
                raise HTTPException(status_code=400, detail="Job description is required when using AI generation.")

            resume_text = await extract_text_from_pdf(resume)
            body_text = await generate_ai_cover_letter(resume_text, job_description)
        else:
            if not custom_content or not custom_content.strip():
                raise HTTPException(status_code=400, detail="Custom cover letter content is required when AI is disabled.")
            body_text = custom_content

        # Split content into paragraphs for the template
        # Ensure paragraphs are clean and non-empty
        paragraphs = [p.strip() for p in body_text.strip().split('\n\n') if p.strip()]
        if not paragraphs:
            # Fallback if AI or custom content results in empty paragraphs
            paragraphs = ["No content generated or provided for the cover letter body."]


        # Get current date
        import datetime
        current_date = datetime.date.today().strftime("%B %d, %Y")


        # Prepare context for Jinja2 template
        template_context = {
            "request": request,
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "employer": employer, # Pass to template
            "job_title": job_title, # Pass to template
            "body_paragraphs": paragraphs,
            "current_date": current_date,
        }

        # Render the HTML content
        # It's better to render using `templates.get_template` for more control
        template = templates.get_template("cover_letter.html")
        rendered_html_str = template.render(template_context)

        # Generate PDF from rendered HTML
        pdf_bytes = weasyprint.HTML(string=rendered_html_str).write_pdf()
        pdf_buffer = io.BytesIO(pdf_bytes)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="cover_letter.pdf"'
            },
        )
    except HTTPException as http_exc:
        # Re-raise FastAPI HTTPExceptions directly
        logger.error(f"HTTPException caught: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        # Catch all other unexpected errors
        logger.exception("An unhandled exception occurred during cover letter generation.")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Simple test endpoint for PDF generation (for debugging WeasyPrint)
@app.get("/test-pdf", response_class=HTMLResponse) # Changed to HTMLResponse for direct view
def test_pdf_view(request: Request):
    """
    Renders a simple HTML page that will be converted to PDF when viewed directly
    or allows manual trigger of PDF download.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test PDF</title>
        <style>
            body { font-family: sans-serif; margin: 2cm; }
            h1 { color: #333; }
            p { line-height: 1.5; }
        </style>
    </head>
    <body>
        <h1>Hello PDF!</h1>
        <p>This is a test PDF generated by WeasyPrint from HTML.</p>
        <p>If you see this page, Jinja2 rendering is working. If you got a PDF earlier, WeasyPrint is also working.</p>
        <a href="/download-test-pdf">Download this as PDF</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/download-test-pdf")
def download_test_pdf():
    """Endpoint to trigger PDF download for testing WeasyPrint."""
    html = "<h1>Hello PDF</h1><p>This is a test PDF.</p>"
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="test.pdf"'}
    )


if __name__ == "__main__":
    import uvicorn
    # Make sure to set your OPENAI_API_KEY environment variable before running!
    # Example (for development, not recommended for production):
    # os.environ["OPENAI_API_KEY"] = "sk-..."
    uvicorn.run(app, host="0.0.0.0", port=8000)