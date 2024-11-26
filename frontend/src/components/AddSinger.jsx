import React, { useState, useEffect } from 'react';

const AddSinger = () => {
    const [name, setName] = useState('');
    const [songs, setSongs] = useState('');
    const [singers, setSingers] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSingers = async () => {
            try {
                const response = await fetch('/api/singers');
                if (!response.ok) throw new Error('Failed to fetch singers');
                const data = await response.json();
                setSingers(data);
            } catch (err) {
                setError(err.message);
                console.error('Fetch error:', err);
            }
        };

        fetchSingers();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        const songArray = songs.split(',').map(song => song.trim());
        const existingSinger = singers.find(singer => singer.name.toLowerCase() === name.toLowerCase());

        try {
            if (existingSinger) {
                const newSongsToAdd = songArray.filter(song => !existingSinger.songs.includes(song));

                if (newSongsToAdd.length === 0) {
                    alert('This combination of singer and songs already exists.');
                    return;
                }

                const response = await fetch(`/api/singers/${existingSinger.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ songs: newSongsToAdd }),
                });

                if (!response.ok) throw new Error('Failed to update singer');
                alert('Songs added to existing singer successfully!');
            } else {
                const response = await fetch('/api/singers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, songs: songArray }),
                });

                if (!response.ok) throw new Error('Failed to add singer');
                alert('Singer added successfully!');
            }

            setName('');
            setSongs('');
        } catch (err) {
            setError(err.message);
            console.error('Submit error:', err);
            alert(err.message);
        }
    };

    return (
        <div>
            <h2>Add Singer</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Name:</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Songs (comma-separated):</label>
                    <input
                        type="text"
                        value={songs}
                        onChange={(e) => setSongs(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Add Singer</button>
            </form>
        </div>
    );
};

export default AddSinger;
