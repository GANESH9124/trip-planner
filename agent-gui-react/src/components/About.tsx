import React from 'react';
import { Link } from 'react-router-dom';

const About: React.FC = () => {
    return (
        <div className="about-container">
            <div className="about-content">
                <h1>✈️ Trip Planner AI</h1>
                <div className="about-section">
                    <h2>About</h2>
                    <p>
                        Welcome to Trip Planner AI, your intelligent travel planning assistant! 
                        Our AI-powered platform helps you create comprehensive vacation plans 
                        tailored to your preferences and needs.
                    </p>
                    <p>
                        Simply describe your dream vacation, and we'll handle the rest - from 
                        creating detailed itineraries to researching destinations, generating 
                        travel guides, and providing expert critiques to ensure your trip is perfect.
                    </p>
                </div>
                
                <div className="about-section">
                    <h2>How It Works</h2>
                    <div className="features-grid">
                        <div className="feature-card">
                            <div className="feature-icon">📋</div>
                            <h3>Plan</h3>
                            <p>Tell us about your vacation ideas and we'll create a detailed plan</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">🔍</div>
                            <h3>Research</h3>
                            <p>We research destinations, activities, and recommendations for you</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">✍️</div>
                            <h3>Generate</h3>
                            <p>Get a comprehensive travel guide and itinerary draft</p>
                        </div>
                        <div className="feature-card">
                            <div className="feature-icon">💭</div>
                            <h3>Refine</h3>
                            <p>Receive expert critiques to perfect your travel plan</p>
                        </div>
                    </div>
                </div>

                <div className="about-section">
                    <h2>Get Started</h2>
                    <p>
                        Ready to plan your next adventure? Head to the main planner and 
                        describe your ideal vacation!
                    </p>
                    <Link to="/" className="cta-button">
                        Start Planning →
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default About;

