import React, { useState, useEffect } from 'react';

const WordHighlighter = ({ sentence, onWordSelect, selected, isClozeImpossible, handleImpossibleClick }) => {

    const [selectedIndex, setSelectedIndex] = useState(selected !== undefined ? selected : null);

  const words = sentence.split(' ');

  useEffect(() => {
    if (selected === null && words.length > 0) {
      setSelectedIndex(null);
    }
  }, [sentence]);

  const handleWordClick = (index) => {
    setSelectedIndex(index);
    const maskedSentence = words.map((word, i) => (i === index ? '<MASK>' : word)).join(' ');
    onWordSelect(maskedSentence, words[index]); // Call the parent callback with the masked sentence
  };


  return (
    <>
      <p>
      <strong>Scientific Statement:</strong>
      </p>
      <div style={{backgroundColor: 'white', border: 'solid black 1px', padding: '5px'}}>
          <div style={{ width: '100%', overflow: 'auto', whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
          {words.map((word, index) => (
              <span
              key={index}
              onClick={() => handleWordClick(index)}
              style={{
                  padding: '5px',
                  cursor: 'pointer',
                  backgroundColor: !isClozeImpossible && index === selectedIndex ? 'yellow' : 'transparent',
                  display: 'inline-block',
              }}
              >
              {word}
              </span>
          ))}
          </div>
      </div>
      </>
  );
};

export default WordHighlighter;
