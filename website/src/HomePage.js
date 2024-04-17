import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import handWithPlant from './images/hotel.png';
import 'bootstrap/dist/css/bootstrap.min.css';

function HomePage() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedCountry, setSelectedCountry] = useState('');
    const [isLoading, setIsLoading] = useState(false); // State to manage loading indicator
    const navigate = useNavigate();
  
    const handleFileChange = (event) => {
      setSelectedFile(event.target.files[0]);
    };
  
    const handleCountrySelection = (country) => {
      setSelectedCountry(country);
    };
  
    const handleSubmit = async (event) => {
      event.preventDefault();
    
      if (!selectedFile || !selectedCountry) {
        alert('Please select a file and a country before submitting.');
        return;
      }
    
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('country', selectedCountry);
    
      // Debugging: Log each key/value pair
      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }
    
      setIsLoading(true); // Start loading indicator before the fetch request
      try {
        const response = await fetch('http://localhost:5000/upload', {
          method: 'POST',
          body: formData,
          // Don't set the Content-Type header
        });
    
        if (response.ok) {
          const result = await response.json();
          console.log(result);
          localStorage.setItem('uploadData', JSON.stringify(result));
          navigate('/buttons', { state: { fileProcessed: true, country: selectedCountry, result: result } });
        } else {
          throw new Error('File upload failed');
        }
      } catch (error) {
        console.error('Error submitting form:', error);
        alert('Error uploading file.');
      } finally {
        setIsLoading(false); // Stop loading indicator after fetch request is complete or fails
      }
    };

    return (
      <div className="app">
        <div className="header">
          <img src={handWithPlant} alt="Go Green" className="header-image" />
          <div className="upload-section">
            <h1>GO GREEN</h1>
            <p>Ready to go Green? Upload your hotel reviews as your first step!</p>
            <form onSubmit={handleSubmit}>
              <div className="file-upload">
                <input
                  type="file"
                  id="fileInput"
                  accept=".xlsx, .csv"
                  onChange={handleFileChange}
                  hidden
                />
                <label htmlFor="fileInput" className="upload-button">
                  Upload Reviews
                </label>
                <span>{selectedFile ? selectedFile.name : 'No file chosen, supported files: xlsx or csv'}</span>
              </div>
              <div className="country-buttons">
                <button
                  type="button"
                  className={`country-button ${selectedCountry === 'Sri Lanka' ? 'selected' : ''}`}
                  onClick={() => handleCountrySelection('Sri Lanka')}
                >
                  Sri Lanka
                </button>
                <button
                  type="button"
                  className={`country-button ${selectedCountry === 'India' ? 'selected' : ''}`}
                  onClick={() => handleCountrySelection('India')}
                >
                  India
                </button>
              </div>
              <button type="submit" className="submit-button" disabled={isLoading}>Submit</button>
            </form>
            {isLoading && <div className="loading-indicator">Loading...</div>} {/* Display loading indicator */}
          </div>
        </div>
      </div>
    );
}

export default HomePage;



