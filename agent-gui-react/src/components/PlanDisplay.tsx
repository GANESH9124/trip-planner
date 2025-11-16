import React from 'react';
import { useLocation } from 'react-router-dom';

interface PlanDisplayProps {
    plan?: string;
}

interface LocationState {
    plan?: string;
}

const PlanDisplay: React.FC<PlanDisplayProps> = ({ plan }) => {
    const location = useLocation();
    const locationState = location.state as LocationState | null | undefined;
    const planFromState = locationState?.plan || plan || 'No plan available';

    return (
        <div className="plan-display">
            <h2>Your Vacation Plan</h2>
            <pre>{planFromState}</pre>
        </div>
    );
};

export default PlanDisplay;