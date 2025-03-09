import React, { useState, useEffect } from 'react';
import ValidationSection from './ValidationSection';
import ApiClient from './ApiClient.js';
import { useAuth } from './contexts/authContext/index.jsx';
import PromptLogin from './PromptLogin.jsx'
import './ValidatorPage.css';
import WordHighlighter from './WordHighlighter.jsx';

const MCtestQuestion = {

  "questions": [
    {
      "question_type": "MCQ",
      "question": "Why are some of the lower values from sky photometry not shown in the merged product?",
      "options": {
        "a": "Because their associated AOD was above 0.3",
        "b": "Because their associated AOD fell below the confidence threshold",
        "c": "Because their associated AOD was exactly at the confidence threshold",
        "d": "Because their associated AOD exceeded the confidence threshold"
      },
      "correct_option": "b"
    }
  ],
  
  "context": "the merged product of \u00060 in Figure 3.4, some of the lower values from sky\nphotometry are not shown, because their associated AOD fell below the con\u0002dence threshold (mid-visible AOD < 0.3) for reliable \u00060 inversions.\nAerosol fields\nFigure 3.3 Mid-visible aerosol optical depth (AOD) at 550 nm wavelength. Comparison between annual maps from global modeling (M), the merged product (X), and\nsun photometer gridded samples (A). Deviations to model simulations suggest AOD\nunderestimates in global modeling.",
  "user_id": null,
  "timestamp_given": null,
  "timestamp_answered": null
}

const FFtestQuestion = {
    "question_type": "FREE_FORM",
    "context": "air–sea interface is locally downward over\nthe eastern equatorial Pacific.\n(e) Mars exhibits a larger diurnal temperature\nrange than Earth; there is almost no diurnal\ncycle in surface temperature on Venus\n(f) Dust storms on Mars substantially reduce the\ndiurnal temperature range, but have little\ninfluence on the daily average temperature.\n(g) Summer insolation (Fig. 10.5) is up to 6%\nstronger in the southern hemisphere than\nin the northern hemisphere.\n(h) The Earth system is nearly in equilibrium\nwith the annual mean net radiation at the\ntop of the atmosphere, but not with the\nseasonal mean net radiation.\n(i) The net radiation at the Earth’s surface\naveraged over the spring or summer\nhemisphere is downward.\n(j) Climatological-mean insolation is greater at\nthe summer pole than on the equator, yet\nsurface air temperatures in the polar region\nare lower than over the equator (Fig. 10.5).\n(k) The net radiation at the top of the\natmosphere over the polar regions is",
    "user_id": null,
    "is_valid": false,
    "question": "What is the relationship between the climatological-mean insolation and surface air temperatures in the polar region compared to the equator?",
    "answer": "Climatological-mean insolation is greater at the summer pole than on the equator, yet surface air temperatures in the polar region are lower than over the equator."
}

const apiClient = new ApiClient();

const ValidatorPage = () => {
  const { currentUser } = useAuth();
  const [validationObj, setValidationObj] = useState({questions:[]});
  const [mcqMode, setMcqMode] = useState(true);
  const [isClozeImpossible, setIsClozeImpossible] = useState(false);
  const [isLoading, setIsLoading] =  useState(false);

  useEffect(() => {
    getNewQuestion(mcqMode);
  }, [mcqMode]);

  const getNewQuestion = async (shouldBeMC) => {
    setIsLoading(true)
    const questionType = shouldBeMC ? "MCQ" : "FREE_FORM";
    try {
      const q_data = await apiClient.getQuestion(questionType); // Assume API returns multiple questions
      if (!q_data) {
        throw new Error("No Data Received");
      }
      q_data.user_id = currentUser.uid;
      q_data.user_email = currentUser.email
      q_data.open_timestamp = new Date().toISOString();
      const questionsWithMeta = q_data.questions.map(question => ({
        ...question,
        user_id: currentUser.uid,
        open_timestamp : new Date().toISOString(),
        submission_timestamp: null
      }));
      q_data.questions = questionsWithMeta;
      q_data.scientific_annotation.term = '';
      // console.log("QDATA", q_data);
      setValidationObj(q_data);
      setIsClozeImpossible(false)
      setIsLoading(false)
    } catch (error) {
      console.error('Error fetching questions:', error);
    }
  };

  const handleSubmit = async () => {
    // console.log(validationObj)

    for (const question of validationObj.questions) {
      if (!question.selected) {
        alert('Please select valid/invalid for each question');
        return;
      }
    }

    if(!isClozeImpossible) {
      if(!validationObj.scientific_annotation.term || validationObj.scientific_annotation.term === "") {
        alert('Please select a scientific term');
        return;
      }
    }

    const question_list = [];
    var isReasonOk = true
    validationObj.questions.forEach(question => {
      const { selected, reason} = question;
      question = {
        ...question,
        is_valid: selected === 'valid'? true: false,
        reason: selected === 'invalid' ? (reason) : null,
        submission_timestamp: new Date().toISOString(),
      };
      if(selected === 'invalid') {
        if(!reason || reason==="") {
          isReasonOk = false
        }
      }
      delete question.selected;
      question_list.push(question);
    });
    if(!isReasonOk) {
      alert('Please provide reason for invalidity');
      return
    }
    validationObj.questions = question_list;
    validationObj.submission_timestamp = new Date().toISOString();
    if (validationObj.scientific_annotation.term != "") {
      validationObj.scientific_annotation.statement = validationObj.scientific_annotation.masked_statement;
      delete validationObj.scientific_annotation.masked_statement;
    }
    // console.log(validationObj);
    alert('Questions submitted');
    apiClient.submitQuestion(validationObj, validationObj["question_type"])
    getNewQuestion(mcqMode);
  };

  function handleWordSelect(masked_sentence, word) {
    validationObj.scientific_annotation = {
      statement: validationObj.scientific_annotation.statement,
      masked_statement: masked_sentence,
      term: word
    }
    setIsClozeImpossible(false)
  }

  const handleImpossibleClick = () => {
    validationObj.scientific_annotation = {
      statement: validationObj.scientific_annotation.statement,
      masked_statement: "",
      term: ""
    }
    setIsClozeImpossible(true)
  }

  const toggleQuestionType = () => {
    setMcqMode(prevMode => !prevMode);
  };

  if (!currentUser) {
    return <PromptLogin />;
  }

  return (
    <>
      <h1>Genie QA Validator</h1>
      <div className='container'>
        <div className='validation-container'>
          <div className='scroll-container'>
          {!isLoading?
            <>
            {validationObj.questions.map((question, index) => (
              <ValidationSection
                key={index}
                validationObj={question}
                onValidationChange={(updatedObj) => {
                  const newValidationObj = {...validationObj}
                  newValidationObj.questions[index] = updatedObj;
                  setValidationObj(newValidationObj);
                }}
                mcqMode={mcqMode}
                handleValidation={(isValid) => {
                  const newValidationObj = {...validationObj};
                  newValidationObj.questions[index].selected = isValid ? 'valid' : 'invalid';
                  setValidationObj(newValidationObj);
                }}
                handleInvalidReason={(reason, otherReason) => {
                  const newValidationObj = {...validationObj}
                  newValidationObj.questions[index].reason = reason;
                  if (reason === 'other') {
                    newValidationObj.questions[index].reason = otherReason;
                  }
                  setValidationObj(newValidationObj);
                  // console.log(newValidationObj)
                }}
                selected={question.selected}
                invalidReason={question.reason}
              />
            ))}
            {validationObj.scientific_annotation ? <WordHighlighter
              sentence={validationObj.scientific_annotation.statement}
              onWordSelect={handleWordSelect}
              isClozeImpossible = {isClozeImpossible}
              handleImpossibleClick = {handleImpossibleClick}
              selected = {null}
            /> : <></>}
            </>
            :
            <>Loading...</>
            }
          </div>
          <div style={{justifyContent:'center', alignItems:'center', display:'flex'}}>
            <button onClick={handleSubmit} className='submit-q-button'>Submit</button>
            <button onClick={toggleQuestionType} className='toggle-button'>
              Toggle Question Type
            </button>
          </div>
        </div>
        <div className='scroll-container' style={{backgroundColor:'#f9f9f9'}}>
            <div className='context'>
            {validationObj.context ? 
              <p><strong>Context: </strong>{validationObj.context.content}
                <br/>
                <br/>
                <strong>Source:</strong> <a href={validationObj.context.link}>{validationObj.context.source}</a>
                <br/>
                <strong>Page:</strong> {validationObj.context.page}
              </p> 
            : 
              <p>Context Unavailable</p>}
          </div>

          {validationObj.retrieved_contexts ?
            validationObj.retrieved_contexts.map((context, index) => (
              <div className='context retrieved'>
                <p><strong>Retrieved Context: </strong>{context.content}
                <br/>
                <br/>
                <strong>Source:</strong> <a href={context.link}>{context.source}</a>
                <br/>
                <strong>Page:</strong> {context.page}
              </p>
              </div>
            ))
          :
              <></>
          }
        </div>
      </div>
    </>
  );
};

export default ValidatorPage;