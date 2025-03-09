import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import ValidatorPage from './ValidatorPage.js';
import AnsweredQuestions from './AnsweredQuestions.jsx';
import ApiClient from './ApiClient.js';
import Login from './Login.js';
import Register from './Register.js';
import { AuthProvider, useAuth } from "./contexts/authContext/index.jsx";
import './App.css';

const apiClient = new ApiClient();

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navigation />
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/validator" element={<ValidatorPage />} />
            <Route path="/answered-questions" element={<AnsweredQuestions/>} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

function Navigation() {
  const { userLoggedIn, doSignOut } = useAuth();

  const handleLogout = async () => {
    try {
      await doSignOut();
      window.location.href = "/login";
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <nav>
      <Link to="/validator">Validator</Link>
      <Link to="/answered-questions">Questions</Link>
      {userLoggedIn && (
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      )}
    </nav>
  );
}

export default App;
