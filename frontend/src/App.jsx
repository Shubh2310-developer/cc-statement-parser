import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import UploadPage from './components/pages/UploadPage';
import ResultsPage from './components/pages/ResultsPage';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

function App() {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <main className="flex-1">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<UploadPage />} />
            <Route path="/results/:jobId" element={<ResultsPage />} />
          </Routes>
        </AnimatePresence>
      </main>

      <Footer />
    </div>
  );
}

export default App;
