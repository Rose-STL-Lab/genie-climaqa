import React from 'react';
import { Link } from 'react-router-dom';
import './PromptLogin.css'; // Import the CSS file

const PromptLogin = () => {
    return (
        <div className="prompt-login-container">
            <div className="prompt-login-box">
                <h2 className="prompt-login-title">Please Log In</h2>
                <p className="prompt-login-message">You need to log in to access this page.</p>
                <Link to="/login" className="prompt-login-button">
                    Log In
                </Link>
            </div>
        </div>
    );
};

export default PromptLogin;
