import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const UploadPage = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/v1/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Navigate to results page with job ID
      navigate(`/results/${response.data.job_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload file');
      setUploading(false);
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: uploading
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4 tracking-tight">
            Credit Card Statement Parser
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload your credit card statement PDF to automatically extract key information with AI-powered accuracy
          </p>
        </div>

        <div
          {...getRootProps()}
          className={`
            border-3 border-dashed rounded-2xl p-16 text-center cursor-pointer
            transition-all duration-300 bg-white shadow-xl
            ${isDragActive ? 'border-primary-500 bg-primary-50 scale-105' : 'border-gray-300 hover:border-primary-400 hover:shadow-2xl'}
            ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />

          {uploading ? (
            <div className="space-y-4">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-500 border-t-transparent mx-auto"></div>
              <p className="text-xl font-semibold text-gray-700">Processing your statement...</p>
              <p className="text-sm text-gray-500">This may take a few seconds</p>
            </div>
          ) : (
            <div className="space-y-4">
              <svg className="mx-auto h-20 w-20 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <div>
                <p className="text-xl font-semibold text-gray-700">
                  {isDragActive
                    ? 'Drop your PDF here'
                    : 'Drag and drop your PDF here'}
                </p>
                <p className="text-gray-500 mt-2">or click to browse</p>
              </div>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>PDF files only • Max 10MB</span>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-6 p-4 bg-error-light border-l-4 border-error rounded-lg animate-slide-down">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-error mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-error-dark font-medium">{error}</p>
            </div>
          </div>
        )}

        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">Supported Banks</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            {[
              { name: 'SBI Card', logo: '/assets/logos/SBI-Logo.png', alt: 'SBI Card Logo' },
              { name: 'HDFC Bank', logo: '/assets/logos/HDFC-Logo.png', alt: 'HDFC Bank Logo' },
              { name: 'ICICI Bank', logo: '/assets/logos/Icici-Logo.png', alt: 'ICICI Bank Logo' },
              { name: 'Axis Bank', logo: '/assets/logos/Axis-Logo.png', alt: 'Axis Bank Logo' },
              { name: 'American Express', logo: '/assets/logos/Amex-Logo.png', alt: 'American Express Logo' }
            ].map((bank) => (
              <div key={bank.name} className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105">
                <div className="h-16 mb-4 flex items-center justify-center">
                  <img
                    src={bank.logo}
                    alt={bank.alt}
                    className="max-h-full max-w-full object-contain"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>';
                    }}
                  />
                </div>
                <div className="font-semibold text-gray-900 text-center text-sm">{bank.name}</div>
                <div className="flex items-center justify-center mt-2">
                  <div className="h-2 w-2 bg-success rounded-full mr-2 animate-pulse"></div>
                  <span className="text-xs text-gray-600">Active</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 bg-white rounded-xl shadow-md p-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What gets extracted?</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              'Card last 4 digits',
              'Card type/variant',
              'Statement period',
              'Payment due date',
              'Total amount due',
              'Minimum payment due'
            ].map((item) => (
              <div key={item} className="flex items-center space-x-3">
                <svg className="h-5 w-5 text-success" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-700">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
