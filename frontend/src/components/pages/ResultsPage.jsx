import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';

const ResultsPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await axios.get(`/api/v1/jobs/${jobId}`);
        setJob(response.data);
        setLoading(false);

        if (response.data.status === 'processing' || response.data.status === 'pending') {
          setTimeout(fetchJob, 2000);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch results');
        setLoading(false);
      }
    };

    fetchJob();
  }, [jobId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-white rounded-2xl shadow-xl p-12">
            <div className="animate-spin rounded-full h-20 w-20 border-4 border-primary-500 border-t-transparent mx-auto mb-6"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Your Statement</h2>
            <p className="text-gray-600">Extracting information with AI-powered accuracy...</p>
            <div className="mt-8 flex justify-center space-x-2">
              <div className="h-2 w-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="h-2 w-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="h-2 w-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-6">
              <svg className="mx-auto h-16 w-16 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h2 className="text-2xl font-bold text-gray-900 mt-4">Processing Failed</h2>
              <p className="text-gray-600 mt-2">{error}</p>
            </div>
            <button
              onClick={() => navigate('/')}
              className="w-full px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-semibold transition-colors"
            >
              Upload Another Statement
            </button>
          </div>
        </div>
      </div>
    );
  }

  const result = job?.result;
  const confidence = result?.confidence_score || 0;

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return 'text-success';
    if (conf >= 0.6) return 'text-warning';
    return 'text-error';
  };

  const getConfidenceBg = (conf) => {
    if (conf >= 0.8) return 'bg-success-light';
    if (conf >= 0.6) return 'bg-warning-light';
    return 'bg-error-light';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <button
          onClick={() => navigate('/')}
          className="mb-6 flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
        >
          <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Upload Another Statement
        </button>

        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 px-8 py-6">
            <h1 className="text-3xl font-bold text-white">Extraction Results</h1>
            <p className="text-primary-100 mt-1">AI-powered statement analysis</p>
          </div>

          <div className="p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Status</div>
                    <div className="text-2xl font-bold text-gray-900 mt-1 capitalize">{job.status}</div>
                  </div>
                  <svg className="h-10 w-10 text-success" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>

              <div className={`rounded-xl p-6 ${getConfidenceBg(confidence)}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-700 font-medium">Overall Confidence</div>
                    <div className={`text-2xl font-bold mt-1 ${getConfidenceColor(confidence)}`}>
                      {(confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                  <svg className={`h-10 w-10 ${getConfidenceColor(confidence)}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>

              <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-700 font-medium">Fields Extracted</div>
                    <div className="text-2xl font-bold text-primary-700 mt-1">{result?.field_count || 0}</div>
                  </div>
                  <svg className="h-10 w-10 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
            </div>

            {result && result.issuer && (
              <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center">
                <svg className="h-6 w-6 text-blue-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                <div>
                  <div className="text-sm text-blue-700 font-medium">Detected Bank</div>
                  <div className="text-lg font-bold text-blue-900 uppercase">{result.issuer}</div>
                </div>
              </div>
            )}

            {result && result.fields && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Extracted Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(result.fields).map(([fieldName, field], index) => (
                    <motion.div
                      key={fieldName}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-primary-300 hover:shadow-lg transition-all"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <div className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
                            {fieldName.replace(/_/g, ' ')}
                          </div>
                          <div className="text-2xl font-bold text-gray-900">
                            {field.value || 'N/A'}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getConfidenceBg(field.confidence)} ${getConfidenceColor(field.confidence)}`}>
                            {(field.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>

                      {field.snippet && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <div className="text-xs font-semibold text-gray-500 mb-1">SOURCE TEXT</div>
                          <div className="text-sm text-gray-700 font-mono">{field.snippet}</div>
                        </div>
                      )}

                      {field.extraction_method && (
                        <div className="mt-2 flex items-center text-xs text-gray-500">
                          <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          Method: {field.extraction_method}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {job.status === 'failed' && job.error_message && (
              <div className="mt-6 p-6 bg-error-light border-l-4 border-error rounded-xl">
                <div className="flex items-start">
                  <svg className="h-6 w-6 text-error mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="font-semibold text-error-dark">Processing Error</h3>
                    <p className="text-error-dark mt-1">{job.error_message}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
