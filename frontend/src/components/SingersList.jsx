import React, { useEffect, useState } from 'react';
import Modal from 'react-modal';

const SingersList = () => {
    const [singers, setSingers] = useState([]);
    const [error, setError] = useState(null);
    const [isEditMode, setIsEditMode] = useState(false);
    const [selectedSingerId, setSelectedSingerId] = useState(null);
    const [selectedSongName, setSelectedSongName] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalType, setModalType] = useState('');

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

    const handleDeleteSinger = async (id) => {
        try {
            const response = await fetch(`/api/singers/${id}`, {
                method: 'DELETE',
            });

            if (!response.ok) throw new Error('Failed to delete singer');

            alert('Singer deleted successfully!');
            setSingers(singers.filter(singer => singer.id !== id));
            closeModal();
        } catch (err) {
            setError(err.message);
            alert(err.message);
        }
    };

    const handleDeleteSong = async (singerId, songName) => {
        try {
            const response = await fetch(`/api/singers/${singerId}/songs/${encodeURIComponent(songName)}`, { // Updated to use /api/
                method: 'DELETE',
            });

            if (!response.ok) throw new Error('Failed to delete song');

            alert('Song deleted successfully!');
            setSingers(singers.map(singer => {
                if (singer.id === singerId) {
                    return { ...singer, songs: singer.songs.filter(song => song !== songName) };
                }
                return singer;
            }));
            closeModal();
        } catch (err) {
            setError(err.message);
            alert(err.message);
        }
    };

    const openModal = (type, singerId, songName) => {
        setModalType(type);
        setSelectedSingerId(singerId);
        setSelectedSongName(songName);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedSingerId(null);
        setSelectedSongName('');
    };

    return (
        <div>
            <h2>Singers List</h2>
            {error && <div style={{ color: 'red' }}>{error}</div>}
            <button onClick={() => setIsEditMode(!isEditMode)}>
                {isEditMode ? 'Exit Edit Mode' : 'Enter Edit Mode'}
            </button>
            {singers.length === 0 ? (
                <p>No singers found.</p>
            ) : (
                <ul>
                    {singers.map(singer => (
                        <li key={singer.id}>
                            <strong>{singer.name}</strong>
                            <ul>
                                {singer.songs.map((song, index) => (
                                    <li key={index}>
                                        {song}
                                        {isEditMode && (
                                            <button onClick={() => openModal('deleteSong', singer.id, song)}>Delete Song</button>
                                        )}
                                    </li>
                                ))}
                            </ul>
                            {isEditMode && (
                                <button onClick={() => openModal('deleteSinger', singer.id)}>Delete Singer</button>
                            )}
                        </li>
                    ))}
                </ul>
            )}

            <Modal
                isOpen={isModalOpen}
                onRequestClose={closeModal}
                ariaHideApp={false}
                style={{
                    overlay: { backgroundColor: 'rgba(0, 0, 0, 0.5)' },
                    content: {
                        top: '50%',
                        left: '50%',
                        right: 'auto',
                        bottom: 'auto',
                        transform: 'translate(-50%, -50%)',
                        padding: '20px',
                        borderRadius: '8px',
                        backgroundColor: '#fff',
                    },
                }}
            >
                <h2>{modalType === 'deleteSinger' ? 'Confirm Delete Singer' : 'Confirm Delete Song'}</h2>
                <p>{modalType === 'deleteSinger' ?
                    'Are you sure you want to delete this singer? All their songs will be deleted as well.' :
                    `Are you sure you want to delete the song "${selectedSongName}"?`}</p>
                <button onClick={() => {
                    if (modalType === 'deleteSinger') {
                        handleDeleteSinger(selectedSingerId);
                    } else if (modalType === 'deleteSong') {
                        handleDeleteSong(selectedSingerId, selectedSongName);
                    }
                }}>
                    Yes
                </button>
                <button onClick={closeModal}>No</button>
            </Modal>
        </div>
    );
};

export default SingersList;
