import React, { useState } from 'react';
import './FeedbackButtons.css';

const FeedbackButtons = ({ 
    sessionId, 
    query, 
    answer, 
    retrievalMethod, 
    retrievalK, 
    rerankThreshold,
    qualityScore,
    confidenceScore,
    responseTime,
    onFeedbackSubmitted 
}) => {
    const [feedback, setFeedback] = useState(null); // 'positive', 'negative', or null
    const [comment, setComment] = useState('');
    const [showComment, setShowComment] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);

    const submitFeedback = async (rating) => {
        if (isSubmitted) return;
        
        setIsSubmitting(true);
        
        try {
            const feedbackData = {
                session_id: sessionId,
                query: query,
                answer: answer,
                rating: rating,
                retrieval_method: retrievalMethod,
                retrieval_k: retrievalK,
                rerank_threshold: rerankThreshold,
                quality_score: qualityScore,
                confidence_score: confidenceScore,
                response_time: responseTime,
                user_comment: comment.trim() || null
            };

            const response = await fetch('/api/feedback/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(feedbackData)
            });

            if (response.ok) {
                const result = await response.json();
                setFeedback(rating);
                setIsSubmitted(true);
                
                if (onFeedbackSubmitted) {
                    onFeedbackSubmitted(rating, result.feedback_id);
                }
                
                // Hide comment box after successful submission
                setTimeout(() => setShowComment(false), 1000);
            } else {
                console.error('Failed to submit feedback');
                alert('Failed to submit feedback. Please try again.');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            alert('Error submitting feedback. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleThumbsUp = () => {
        if (isSubmitted) return;
        submitFeedback('positive');
    };

    const handleThumbsDown = () => {
        if (isSubmitted) return;
        setShowComment(true);
        setFeedback('negative');
    };

    const handleCommentSubmit = () => {
        submitFeedback('negative');
    };

    return (
        <div className="feedback-buttons">
            <div className="feedback-actions">
                <button
                    className={`feedback-btn ${feedback === 'positive' ? 'active positive' : ''} ${isSubmitted ? 'submitted' : ''}`}
                    onClick={handleThumbsUp}
                    disabled={isSubmitting || isSubmitted}
                    title={isSubmitted ? 'Feedback submitted' : 'This answer was helpful'}
                >
                    👍
                    {feedback === 'positive' && <span className="feedback-status">✓</span>}
                </button>
                
                <button
                    className={`feedback-btn ${feedback === 'negative' ? 'active negative' : ''} ${isSubmitted ? 'submitted' : ''}`}
                    onClick={handleThumbsDown}
                    disabled={isSubmitting || isSubmitted}
                    title={isSubmitted ? 'Feedback submitted' : 'This answer needs improvement'}
                >
                    👎
                    {feedback === 'negative' && isSubmitted && <span className="feedback-status">✓</span>}
                </button>

                {isSubmitting && (
                    <span className="feedback-loading">Submitting...</span>
                )}
            </div>

            {showComment && !isSubmitted && (
                <div className="feedback-comment-box">
                    <textarea
                        placeholder="Optional: Tell us how we can improve this answer..."
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        rows={3}
                        maxLength={500}
                        className="feedback-comment-input"
                    />
                    <div className="feedback-comment-actions">
                        <button
                            onClick={handleCommentSubmit}
                            disabled={isSubmitting}
                            className="feedback-submit-btn"
                        >
                            Submit Feedback
                        </button>
                        <button
                            onClick={() => setShowComment(false)}
                            disabled={isSubmitting}
                            className="feedback-cancel-btn"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {isSubmitted && (
                <div className="feedback-success">
                    <span className="feedback-success-text">
                        ✓ Thank you for your feedback! This helps improve our system.
                    </span>
                </div>
            )}
        </div>
    );
};

export default FeedbackButtons; 