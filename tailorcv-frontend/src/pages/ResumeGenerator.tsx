import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Upload, 
  FileText, 
  Linkedin, 
  Download, 
  Eye, 
  Loader2,
  CheckCircle,
  AlertCircle 
} from 'lucide-react';

const ResumeGenerator: React.FC = () => {
  const [inputType, setInputType] = useState<'linkedin' | 'upload'>('linkedin');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState('');
  const [email, setEmail] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResumeUrl, setGeneratedResumeUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024) {
        setUploadedFile(file);
        setError(null);
      } else {
        setError('Please upload a PDF file under 10MB');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('jobDescription', jobDescription);
      formData.append('email', email);
      
      if (inputType === 'linkedin') {
        formData.append('linkedinUrl', linkedinUrl);
      } else if (uploadedFile) {
        formData.append('resume', uploadedFile);
      }

      const response = await fetch('/api/generate-resume', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        setGeneratedResumeUrl(data.resumeUrl);
      } else {
        setError(data.error || 'Failed to generate resume');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const isFormValid = () => {
    if (!jobDescription.trim()) return false;
    if (inputType === 'linkedin') {
      return linkedinUrl.trim() !== '';
    } else {
      return uploadedFile !== null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="mb-8">
            <Link 
              to="/" 
              className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Home
            </Link>
            <h1 className="text-3xl sm:text-4xl font-display font-bold text-gray-900 mb-2">
              Generate Your Resume
            </h1>
            <p className="text-lg text-gray-600">
              Upload your data and job description to create a tailored, ATS-friendly resume
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-8">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Choose your input method
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setInputType('linkedin')}
                    className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                      inputType === 'linkedin'
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center">
                      <Linkedin className="w-6 h-6 text-blue-600 mr-3" />
                      <div className="text-left">
                        <h3 className="font-medium text-gray-900">LinkedIn Profile</h3>
                        <p className="text-sm text-gray-600">Enter your LinkedIn URL</p>
                      </div>
                    </div>
                  </button>
                  
                  <button
                    type="button"
                    onClick={() => setInputType('upload')}
                    className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                      inputType === 'upload'
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center">
                      <Upload className="w-6 h-6 text-gray-600 mr-3" />
                      <div className="text-left">
                        <h3 className="font-medium text-gray-900">Upload Resume</h3>
                        <p className="text-sm text-gray-600">Upload your PDF resume</p>
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {inputType === 'linkedin' ? (
                <div>
                  <label htmlFor="linkedin-url" className="block text-sm font-medium text-gray-700 mb-2">
                    LinkedIn Profile URL
                  </label>
                  <input
                    type="url"
                    id="linkedin-url"
                    value={linkedinUrl}
                    onChange={(e) => setLinkedinUrl(e.target.value)}
                    placeholder="https://linkedin.com/in/yourprofile"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    required
                  />
                </div>
              ) : (
                <div>
                  <label htmlFor="resume-upload" className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Resume (PDF, max 10MB)
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                    <input
                      type="file"
                      id="resume-upload"
                      accept=".pdf"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                    <label
                      htmlFor="resume-upload"
                      className="cursor-pointer flex flex-col items-center"
                    >
                      {uploadedFile ? (
                        <div className="flex items-center text-green-600">
                          <CheckCircle className="w-8 h-8 mr-2" />
                          <span className="font-medium">{uploadedFile.name}</span>
                        </div>
                      ) : (
                        <>
                          <FileText className="w-12 h-12 text-gray-400 mb-2" />
                          <span className="text-gray-600">Click to upload or drag and drop</span>
                        </>
                      )}
                    </label>
                  </div>
                </div>
              )}

              <div>
                <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description
                </label>
                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  rows={8}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                  required
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address (Optional)
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
                <p className="text-sm text-gray-500 mt-1">
                  We'll email you the resume if provided (optional)
                </p>
              </div>

              {error && (
                <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-700">{error}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!isFormValid() || isGenerating}
                className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white py-4 px-6 rounded-lg font-semibold text-lg transition-colors duration-200 flex items-center justify-center"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Generating Resume...
                  </>
                ) : (
                  'Generate Resume'
                )}
              </button>
            </form>

            {generatedResumeUrl && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg"
              >
                <div className="flex items-center mb-4">
                  <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
                  <h3 className="text-lg font-semibold text-green-800">
                    Resume Generated Successfully!
                  </h3>
                </div>
                <div className="flex flex-col sm:flex-row gap-4">
                  <a
                    href={generatedResumeUrl}
                    download
                    className="flex items-center justify-center bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    <Download className="w-5 h-5 mr-2" />
                    Download PDF
                  </a>
                  <button
                    onClick={() => window.open(generatedResumeUrl, '_blank')}
                    className="flex items-center justify-center border border-primary-600 text-primary-600 hover:bg-primary-50 px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    <Eye className="w-5 h-5 mr-2" />
                    Preview
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ResumeGenerator;