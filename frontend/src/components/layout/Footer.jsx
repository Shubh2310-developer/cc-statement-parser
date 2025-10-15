import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-gray-600">
            &copy; 2025 CC Statement Parser. Built with FastAPI & React.
          </div>

          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span className="font-semibold text-gray-800">Supported Banks:</span>
            <div className="flex space-x-2">
              <span className="px-2 py-1 bg-primary-50 text-primary-700 rounded">HDFC</span>
              <span className="px-2 py-1 bg-primary-50 text-primary-700 rounded">ICICI</span>
              <span className="px-2 py-1 bg-primary-50 text-primary-700 rounded">Axis</span>
              <span className="px-2 py-1 bg-primary-50 text-primary-700 rounded">Amex</span>
              <span className="px-2 py-1 bg-primary-50 text-primary-700 rounded">SBI</span>
            </div>
          </div>
        </div>

        <div className="mt-4 text-center text-xs text-gray-500">
          Powered by PyMuPDF • Camelot • Tesseract OCR
        </div>
      </div>
    </footer>
  );
};

export default Footer;
