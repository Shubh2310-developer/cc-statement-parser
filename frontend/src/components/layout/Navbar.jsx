import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-3">
            <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <span className="text-xl font-bold text-gray-900">CC Statement Parser</span>
          </Link>

          <div className="flex items-center space-x-6">
            <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
              Upload
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
            >
              API Docs
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
