import React, { useState, useEffect } from 'react';
import './FeedbackPage.css';

const FeedbackPage = () => {
    const [feedbackSummary, setFeedbackSummary] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchFeedbackData();
    }, []);

    const fetchFeedbackData = async () => {
        try {
            const response = await fetch('/api/feedback/summary?hours=24', {
                credentials: 'include'
            });
            if (response.ok) {
                const data = await response.json();
                setFeedbackSummary(data.data);
            }
        } catch (err) {
            console.error('Error fetching feedback:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="feedback-page">Loading...</div>;
    }

    return (
        <div className="feedback-page">
            <h1>Feedback Analytics</h1>
            <div className="feedback-summary">
                <div className="summary-card">
                    <h3>Total Feedback</h3>
                    <div className="value">{feedbackSummary?.total_feedback || 0}</div>
                </div>
                <div className="summary-card positive">
                    <h3>Positive</h3>
                    <div className="value">{feedbackSummary?.positive_count || 0}</div>
                </div>
                <div className="summary-card negative">
                    <h3>Negative</h3>
                    <div className="value">{feedbackSummary?.negative_count || 0}</div>
                </div>
            </div>
        </div>
    );
};

export default FeedbackPage; 