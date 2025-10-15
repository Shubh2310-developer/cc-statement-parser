import React from 'react';
import { useNavigate } from 'react-router-dom';

const PreviewPage = () => {
  const navigate = useNavigate();

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:text-blue-800 flex items-center"
        >
          ← Back to Upload
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold mb-4">PDF Preview</h1>
        <p className="text-gray-600">PDF preview functionality coming soon...</p>
      </div>
    </div>
  );
};

export default PreviewPage;
