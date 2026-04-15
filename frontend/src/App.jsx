import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router';
import InputPage from './pages/InputPage';
import TimelinePage from './pages/TimelinePage';
import DetailPage from './pages/DetailPage';
import './App.css';

const Navigation = () => {
  const location = useLocation();
  return (
    <nav className="app-nav">
      <Link to="/" className={location.pathname === '/' ? 'active' : ''}>작성하기</Link>
      <Link to="/timeline" className={location.pathname === '/timeline' ? 'active' : ''}>타임라인</Link>
    </nav>
  );
};

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <header className="app-header">
          <Link to="/" className="app-title">NARA's DIARY</Link>
          <Navigation />
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<InputPage />} />
            <Route path="/timeline" element={<TimelinePage />} />
            <Route path="/post/:id" element={<DetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
