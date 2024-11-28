// src/components/Home.jsx
import React from 'react';

const Home = () => {
    return (
        <div style={{ textAlign: 'center', padding: '20px' }}>
            <h1>Baruchi Welcome to Daniel's Music App!</h1>
            <img src="/home-image.jpg" alt="Music Logo" style={{ width: '300px', height: 'auto' }} />
            <p>Explore your favorite singers and their songs!</p>
        </div>
    );
};

export default Home;