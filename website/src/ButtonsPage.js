import React from 'react';
import './ButtonPage.css';
import imageSource from './images/bik.svg';
import { useNavigate } from 'react-router-dom';

function ButtonsPage() {
    console.log("Rendering ButtonsPage component");
    const navigate = useNavigate();

    const navigateHome = () => {
        navigate('/');
    };

     const handleButtonClick = (aspect) => {
        console.log("Button clicked:", aspect);
        const storedData = JSON.parse(localStorage.getItem('uploadData') || '{}');
        console.log("Stored Data:", storedData);
        console.log('hi');
        console.log({ state: { data: storedData[aspect], aspect: aspect } })
        navigate(`/summary?aspect=${aspect}`, { state: { data: storedData[aspect], aspect: aspect } });
     }

    const handleReuploadClick = () => {
        // Assuming you store the path in localStorage or you need to adjust this logic
        const filePath = localStorage.getItem('uploadedFilePath');

        fetch('http://localhost:5000/delete-file', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filePath })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            navigateHome();  // Navigate home or refresh the page as needed
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
    return (
        <div className="buttons-page">
                        {/* New home button below the image section */}
                        <div className="">
                <button onClick={navigateHome} className="home-button">Reupload reviews</button>
            </div>
                

            <div className="image-section">

                <h2 className="tagline">Pick the aspect to get the sustainable strategies</h2>


                <img className="bottom-left-image" src={imageSource} alt="Descriptive Alt Text" />


                <div className="button-section">
                    <button onClick={() => handleButtonClick('food')}>Food</button>
                    <button onClick={() => handleButtonClick('Geo-context')}>Geo-Context</button>
                    <button onClick={() => handleButtonClick('Guest-relations')}>Guest-relations</button>
                    
                </div>


            </div>


            
        </div>
    );
}

export default ButtonsPage;



