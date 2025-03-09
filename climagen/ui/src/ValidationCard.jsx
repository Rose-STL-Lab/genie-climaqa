import { useState, useEffect } from 'react';
import React from 'react';
import './ValidationCard.css';

const ValidationCard = ({ 
    validation, 
    selected, 
    isMC,
    handleValidation,
    handleInvalidReason,
    invalidReason
}) => {
    const [otherReason, setOtherReason] = useState('');
    const [isReasionOther, setIsReasonOther] = useState(false);

    useEffect(() => {
        handleInvalidReason('other', otherReason);
      }, [otherReason]);

    if (!validation) {
        return (
            <div className="question">
                <p>Waiting for question...</p>
            </div>
        )
    }

    if ((isMC && !validation.options) || (!isMC && !validation.answer)) {
        return (
            <div className="question">
                <p>Loading...</p>
            </div>
        )
    }

    return (
        <div className={`question ${selected}`}>
            <div>
                <p><strong>Complexity: </strong> {validation.question_complexity}</p>
                <br/>
                <p><strong>Question: </strong> {validation.question}</p>
            </div>

            {isMC ? (
                <div>
                    <br/>
                    {Object.entries(validation.options).map(([key, answer]) => (
                        <p key={key} className={key === validation.correct_option ? 'correct-answer' : ''}>
                            {key === validation.correct_option && <span className='checkmark'>✓</span>} {key}) {answer}
                        </p>
                    ))}
                </div>
            ) : (
                <div>
                    <p><strong>Answer: </strong>{validation.answer}</p>
                </div>
            )}
            <div className='yesnobuttons'>
                <button className='invalid-button' onClick={() => handleValidation(false)}>Invalid</button>
                <button className='valid-button' onClick={() => handleValidation(true)}>Valid</button>
            </div>
            {selected === 'invalid' && (
                <div className='invalid-reasons'>
                <p><strong>Please select reason for invalidity:</strong></p>
                <button
                    className={invalidReason === 'bad context' ? 'selected' : ''}
                    onClick={() => {setIsReasonOther(false); handleInvalidReason('bad context', otherReason)}}
                >
                    Bad Context
                </button>
                <button
                    className={invalidReason === 'wrong answer' ? 'selected' : ''}
                    onClick={() => {setIsReasonOther(false); handleInvalidReason('wrong answer', otherReason)}}
                >
                    Wrong Answer
                </button>
                <button
                    className={invalidReason === 'not enough information' ? 'selected' : ''}
                    onClick={() => {setIsReasonOther(false); handleInvalidReason('not enough information', otherReason)}}
                >
                    Not Enough Information
                </button>
                <button
                    className={invalidReason === 'question doesn\'t make sense' ? 'selected' : ''}
                    onClick={() => {setIsReasonOther(false); handleInvalidReason('question doesn\'t make sense', otherReason)}}
                >
                    Question Doesn't Make Sense
                </button>
                <button
                    className={isReasionOther ? 'selected' : ''}
                    onClick={() => {setIsReasonOther(true); handleInvalidReason('other', otherReason)}}
                >
                    Other
                </button>
                {isReasionOther && (
                    <textarea
                    style={{boxSizing:'border-box'}}
                    value={otherReason}
                    onChange={(e) => setOtherReason(e.target.value)}
                    placeholder='Please specify the reason...'
                    />
                )}
                </div>
            )}
        </div>
    );
}

export default ValidationCard;
