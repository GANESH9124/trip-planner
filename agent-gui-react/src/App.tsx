import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ChatWindow from './components/ChatWindow';
import PlanDisplay from './components/PlanDisplay';
import ResearchPanel from './components/ResearchPanel';
import About from './components/About';
import './styles/App.css';

const App: React.FC = () => {
    return (
        <Router>
            <div className="App">
                <nav className="navbar">
                    <div className="nav-container">
                        <Link to="/" className="nav-logo">
                            ✈️ Trip Planner AI
                        </Link>
                        <div className="nav-links">
                            <Link to="/" className="nav-link">Planner</Link>
                            <Link to="/plan" className="nav-link">My Plans</Link>
                            <Link to="/research" className="nav-link">Research</Link>
                            <Link to="/about" className="nav-link">About</Link>
                        </div>
                    </div>
                </nav>
                <Routes>
                    <Route path="/" element={<ChatWindow />} />
                    <Route path="/plan" element={<PlanDisplay />} />
                    <Route path="/research" element={<ResearchPanel />} />
                    <Route path="/about" element={<About />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;