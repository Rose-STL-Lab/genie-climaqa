import React, { useState } from 'react';
import { Navigate, Link, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/authContext';
import { doCreateUserWithEmailAndPassword } from './firebase/auth';
import './Register.css'; // Import the CSS file

const Register = () => {
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isRegistering, setIsRegistering] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const { userLoggedIn } = useAuth();

    const onSubmit = async (e) => {
        e.preventDefault();
        if (!isRegistering) {
            setIsRegistering(true);
            await doCreateUserWithEmailAndPassword(email, password).catch((error) => {
                setErrorMessage(error.message);
                setIsRegistering(false);
            });
        }
    };

    return (
        <>
            {userLoggedIn && <Navigate to='/validator' replace={true} />}

            <main className="register-container">
                <div className="register-box">
                    <div className="text-center mb-6">
                        <div className="mt-2">
                            <h3 className="register-title">Create a New Account</h3>
                        </div>
                    </div>
                    <form onSubmit={onSubmit} className="register-form">
                        <div>
                            <label className="register-label">Email</label>
                            <input
                                type="email"
                                autoComplete="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="register-input"
                            />
                        </div>

                        <div>
                            <label className="register-label">Password</label>
                            <input
                                disabled={isRegistering}
                                type="password"
                                autoComplete="new-password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="register-input"
                            />
                        </div>

                        <div>
                            <label className="register-label">Confirm Password</label>
                            <input
                                disabled={isRegistering}
                                type="password"
                                autoComplete="off"
                                required
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="register-input"
                            />
                        </div>

                        {errorMessage && (
                            <span className="error-message">{errorMessage}</span>
                        )}

                        <button
                            type="submit"
                            disabled={isRegistering}
                            className={`submit-button ${isRegistering ? 'disabled' : ''}`}
                        >
                            {isRegistering ? 'Signing Up...' : 'Sign Up'}
                        </button>
                        <div className="text-sm text-center">
                            Already have an account?{' '}
                            <Link to='/login' className="login-link">Continue</Link>
                        </div>
                    </form>
                </div>
            </main>
        </>
    );
};

export default Register;
