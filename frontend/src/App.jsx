// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './components/Home';
import SingersList from './components/SingersList';
import AddSinger from './components/AddSinger';
import './App.css'; // Import your CSS file
import './index.css'; // Import global styles

const App = () => {
    return (
        <Router>
            <nav>
                <Link to="/">Home</Link>
                <Link to="/singers">Singers List</Link>
                <Link to="/add-singer">Add Singer</Link>
            </nav>

            <div className="container">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/singers" element={<SingersList />} />
                    <Route path="/add-singer" element={<AddSinger />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;