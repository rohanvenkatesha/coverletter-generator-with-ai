import { useState, useRef } from 'react'
import axios from 'axios'

function FileUpload({ onFileSelect }: { onFileSelect: (file: File | null) => void }) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState<string>('')

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setFileName(file?.name || '')
    onFileSelect(file)
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={handleClick}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none"
      >
        Choose Resume PDF
      </button>
      {fileName && <span className="text-gray-700">{fileName}</span>}
      <input
        type="file"
        accept=".pdf"
        ref={fileInputRef}
        onChange={handleChange}
        className="hidden"
      />
    </div>
  )
}

export default function UploadForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    linkedin: '',
    github: '',
    portfolio: '',
    employer: '', // <-- This needs to be passed to backend
    job_title: '', // <-- This needs to be passed to backend
    custom_content: '',
    job_description: '',
  })
  const [resume, setResume] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [useAI, setUseAI] = useState(false)
  const [error, setError] = useState<string | null>(null) // State for displaying errors

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const toggleUseAI = () => {
    setUseAI(!useAI)
    // Clear relevant fields when toggling AI
    setFormData({
      ...formData,
      custom_content: '',
      job_description: '',
    })
    setResume(null)
    setError(null); // Clear any previous errors
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null); // Clear previous errors on new submission

    if (useAI) {
      if (!resume) {
        setError('Please upload your resume PDF.');
        return;
      }
      if (!formData.job_description.trim()) {
        setError('Please enter the job description.');
        return;
      }
    } else {
      if (!formData.custom_content.trim()) {
        setError('Please enter your custom cover letter content or enable AI generation.');
        return;
      }
    }

    const data = new FormData()
    Object.entries(formData).forEach(([key, val]) => {
      // Append only if value is not empty string, especially for optional fields
      if (val !== null && val !== undefined && val !== '') {
        data.append(key, val);
      }
    });

    if (resume) data.append('resume', resume);
    data.append('use_ai', String(useAI)); // Ensure boolean is sent as string

    setLoading(true)
    try {
      const res = await axios.post('http://localhost:8000/generate', data, {
        responseType: 'blob',
      })
      const blob = new Blob([res.data], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)

      // Auto trigger download
      const a = document.createElement('a')
      a.href = url
      a.download = 'cover_letter.pdf'
      document.body.appendChild(a)
      a.click()
      a.remove()

      URL.revokeObjectURL(url)
    } catch (err: any) { // Type 'any' for simpler error handling here
      console.error('Submission error:', err)
      if (err.response && err.response.data) {
        // Attempt to read error message from backend
        try {
          const errorBlob = new Blob([err.response.data], { type: 'application/json' });
          const reader = new FileReader();
          reader.onload = function(event) {
            if (event.target && typeof event.target.result === 'string') {
              const errorData = JSON.parse(event.target.result);
              setError(errorData.detail || 'An unexpected error occurred from the server.');
            }
          };
          reader.readAsText(errorBlob);
        } catch (parseError) {
          setError('An unexpected error occurred. Could not parse server error message.');
        }
      } else {
        setError('Something went wrong. Please check your network connection and the server status.');
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white rounded shadow space-y-4">
      <div className="flex items-center gap-3">
        <input
          id="use-ai"
          type="checkbox"
          checked={useAI}
          onChange={toggleUseAI}
          className="h-5 w-5"
        />
        <label htmlFor="use-ai" className="select-none font-semibold">
          Use AI to Generate Cover Letter
        </label>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

      <input
        name="name"
        placeholder="Your Name"
        required
        onChange={handleChange}
        className="input"
        value={formData.name}
      />
      <input
        name="email"
        type="email"
        placeholder="Your Email"
        required
        onChange={handleChange}
        className="input"
        value={formData.email}
      />
      <input
        name="phone"
        placeholder="Phone Number"
        required
        onChange={handleChange}
        className="input"
        value={formData.phone}
      />
      <input
        name="linkedin"
        placeholder="LinkedIn URL (optional)"
        onChange={handleChange}
        className="input"
        value={formData.linkedin}
      />
      <input
        name="github"
        placeholder="GitHub URL (optional)"
        onChange={handleChange}
        className="input"
        value={formData.github}
      />
      <input
        name="portfolio"
        placeholder="Portfolio URL (optional)"
        onChange={handleChange}
        className="input"
        value={formData.portfolio}
      />
      <input
        name="employer"
        placeholder="Employer Name"
        required
        onChange={handleChange}
        className="input"
        value={formData.employer}
      />
      <input
        name="job_title"
        placeholder="Job Title"
        required
        onChange={handleChange}
        className="input"
        value={formData.job_title}
      />

      {useAI ? (
        <>
          <textarea
            name="job_description"
            rows={6}
            placeholder="Paste the Job Description here (no word limit)"
            required
            onChange={handleChange}
            value={formData.job_description}
            className="textarea"
          />
          <FileUpload onFileSelect={setResume} />
        </>
      ) : (
        <textarea
          name="custom_content"
          rows={6}
          placeholder="Paste your custom cover letter content here"
          required
          onChange={handleChange}
          value={formData.custom_content}
          className="textarea"
        />
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Generating...' : 'Generate Cover Letter'}
      </button>
    </form>
  )
}