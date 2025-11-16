import React, { useState } from 'react';
import { fetchResearchData } from '../services/agentService';

interface ResearchData {
    queries: string[];
    answers: string[];
}

const ResearchPanel: React.FC = () => {
    const [researchData, setResearchData] = useState<ResearchData | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [planInput, setPlanInput] = useState<string>('');

    const handleResearch = async () => {
        if (!planInput.trim()) {
            setError('Please enter a plan to research.');
            return;
        }

        setLoading(true);
        setError(null);
        setResearchData(null);

        try {
            const data = await fetchResearchData(planInput.trim());
            setResearchData({ queries: data.queries || [], answers: data.answers || [] });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load research data.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="research-panel">
            <h2>Research Data</h2>
            <p>Enter a vacation plan to research destinations, activities, and recommendations.</p>
            
            <div className="research-input-section">
                <textarea
                    value={planInput}
                    onChange={(e) => setPlanInput(e.target.value)}
                    placeholder="Enter your vacation plan here..."
                    className="research-textarea"
                    rows={5}
                    disabled={loading}
                />
                <button 
                    onClick={handleResearch} 
                    disabled={loading || !planInput.trim()}
                    className="research-button"
                >
                    {loading ? 'Researching...' : 'Research Plan'}
                </button>
            </div>

            {error && (
                <div className="error">
                    {error}
                    {error.includes('Network') || error.includes('ECONNREFUSED') || error.includes('Failed to fetch') ? (
                        <div style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                            <p>Make sure the backend server is running on {process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000'}</p>
                        </div>
                    ) : null}
                </div>
            )}

            {researchData && (
                <>
                    <h3>Research Queries</h3>
                    {researchData.queries && researchData.queries.length > 0 ? (
                        <ul>
                            {researchData.queries.map((item, index) => (
                                <li key={index}>{item}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>No queries generated.</p>
                    )}
                    
                    <h3>Research Answers</h3>
                    {researchData.answers && researchData.answers.length > 0 ? (
                        <ul>
                            {researchData.answers.map((item, index) => (
                                <li key={index}>{item}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>No answers found.</p>
                    )}
                </>
            )}
        </div>
    );
};

export default ResearchPanel;