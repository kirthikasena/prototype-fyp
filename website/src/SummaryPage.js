import React from 'react';
import './Summary.css';
import handWithPlant from './images/sus-5.gif';
import { useNavigate, useLocation } from 'react-router-dom';

const SummaryPage = () => {
  const location = useLocation(); // Correct use of useLocation
  const data = location.state?.result;
  console.log(data)
  const aspect = location.state?.aspect;
  const aspectData = location.state?.data;
  const { summary, strategies } = aspectData;
  const navigate = useNavigate();

  const formatText = (text) => {
    // Splitting by new lines
    const lines = text.split('\n');
    
    return lines.map((line, index) => {
      // Check if the line starts with a bullet point pattern (e.g., "1. **Title**:")
      const bulletPointMatch = line.match(/^\d+\.\s\*\*(.*?)\*\*:/);
      
      if (bulletPointMatch) {
        // If it's a bullet point, format the title as bold and add the rest of the line
        const title = bulletPointMatch[1]; // Capturing the title part
        const description = line.substring(bulletPointMatch[0].length); // The rest of the line after the title
        
        return (
          <div key={index} style={{ marginBottom: '5px' }}> {/* Add a small space between bullet points */}
            <strong>{`${bulletPointMatch[0]}`}</strong> {/* Display the number and title in bold */}
            {description}
          </div>
        );
      } else {
        // For lines that do not start with a bullet point pattern, just return the line
        return (
          <span key={index}>
            {line}
            <br />
          </span>
        );
      }
    });
  };


    // Initialize solutionText and reasoningText
    let solutionText = "Solution not available";
    let reasoningText = "Reasoning not available";


  // Check if strategies contains the "reasoning :" substring
  const solutionIndex = strategies?.indexOf("Solution :");

  let solutionStartIndex = strategies.indexOf("Solution:");
  console.log(solutionStartIndex)
  if (!solutionStartIndex) {
    // If "Solution:" was not found, look for the alternative
    solutionStartIndex = strategies.indexOf("aspect': 'Geo-context'}");
  }

  const separatorIndex = strategies.indexOf("****************************************", solutionStartIndex);



  const reasoningIndex = strategies?.indexOf("reasoning :");

  if (solutionStartIndex !== -1 && separatorIndex !== -1) {
    solutionText = strategies.substring(solutionStartIndex+9, separatorIndex).trim();
  }


  if (reasoningIndex > -1) {
    // Extract solution and reasoning texts based on the index of "reasoning :"
    // solutionText = strategies.substring(solutionIndex, reasoningIndex).trim();
    reasoningText = strategies.substring(reasoningIndex + "reasoning :".length).trim();
  } 
  else {
    // If "reasoning :" is not found, use the whole string as the solutionText
    const reasoningIndex = strategies?.indexOf("reasoning:");
    reasoningText = strategies.substring(reasoningIndex + "reasoning :".length).trim();
  }


  const handleBackClick = () => {
    navigate('/buttons');
  };

  return (
    <div className="main-container">
      <div className="summary-container">
        <img src={handWithPlant} alt="Go Green" className="bottom-right-image" />
        <button onClick={handleBackClick} className="back-button">Back</button>
        <div className="content-container">
          <div className="summary">
            <h2>{`Summary for ${aspect}`}</h2>
            <p>{formatText(summary)}</p> {/* Apply formatting to summary */}
          </div>
          <div className="strategies">
            <h2>Solution</h2>
            {formatText(solutionText)}
            <h2>Reasoning</h2>
            {formatText(reasoningText)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryPage;


