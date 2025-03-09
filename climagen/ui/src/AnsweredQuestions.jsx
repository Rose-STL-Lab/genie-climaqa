import React, { useState, useEffect } from 'react';
import { useAuth } from './contexts/authContext';
import PromptLogin from './PromptLogin';
import ApiClient from './ApiClient';
import './AnsweredQuestions.css';
import WordHighlighterUpdate from './WordHighlighterUpdate';

const apiClient = new ApiClient();

const AnsweredQuestions = () => {
  const { currentUser } = useAuth();
  const [questionType, setQuestionType] = useState('MCQ')
  const [validations, setValidations] = useState([]);
  const [reasons, setReasons] = useState({});
  const [stats, setStats] = useState({});
  const [showContext, setShowContext] = useState({});
  const [contextObjs, setContextObjs] = useState({});

  useEffect(() => {
    if (currentUser) {
      getQuestionsFromUser();
    }
  }, [currentUser, questionType]);

  const handleValidationChange = async (index, isValid) => {
    if (window.confirm("Are you sure you want to change your answer?")) {
      const updatedValidations = validations.map((item, i) => {
        if (i === index) {
          return { ...item, is_valid: isValid };
        }
        return item;
      });
      setValidations(updatedValidations);
      if(isValid) {
        setReasons((prev) => ({
          ...prev,
          [index]: "",
        }));
      }

      const question = validations[index];
      await apiClient.updateQuestion(
        question.id,
        isValid,
        question.question_type,
        reasons[index]
      );
    }
  };

  const handleReasonBlur = async (index) => {
    if (window.confirm("Are you sure you want to update the reason?")) {
      const question = validations[index];
      await apiClient.updateQuestion(
        question.id,
        question.is_valid,
        question.question_type,
        reasons[index]
      );
    }
  };

  const handleReasonChange = (index, value) => {
    setReasons((prev) => ({
      ...prev,
      [index]: value,
    }));
  };

  const handleContextChange = async (index, item) => {
    if(!showContext[index] && !(index in contextObjs)) {
      await getContexts(index, item.context_id, item.retrieved_context_ids); 
    }
    setShowContext((prev) => ({
      ...prev,
      [index]: !showContext[index],
    }));
  };

  const handleDropdownChange = (event) => {
    setQuestionType(event.target.value); // Update state with selected value
  };

  const getContexts = async (index, context_id, retrieved_context_ids) => {
    const obj = {}
    const context_ids = [context_id]

    retrieved_context_ids.forEach(id => {
      // console.log(id)
      context_ids.push(id)
    });
    const contexts = await apiClient.getContexts(context_ids);
    // console.log(contexts)
    obj['context'] = contexts[context_id]
    obj['retrieved_contexts'] = []
    retrieved_context_ids.forEach(id => {
      obj['retrieved_contexts'].push(contexts[id])
    });
    setContextObjs((prev) => ({
      ...prev,
      [index]: obj,
    }));
  }

  const getQuestionsFromUser = async () => {
    // console.log(questionType)
    const questions = await apiClient.getQuestionsForUser(currentUser.uid, questionType);
    const questionWithId = Object.keys(questions).map(key => ({
        ...questions[key],
        id: key
      }));

    const combinedQuestions = [...questionWithId];
    combinedQuestions.sort((a, b) => {
      const timestampA = a.submission_timestamp ? new Date(a.submission_timestamp).getTime() : 0;
      const timestampB = b.submission_timestamp ? new Date(b.submission_timestamp).getTime() : 0;
      return timestampB - timestampA;
    });
    setValidations(combinedQuestions);

    if (questionType != "CLOZE") {
      // Initialize invalidReason and otherReason states based on fetched data
      const initialReasons = {};
      const initialShowContext = {}

      var numValid = 0
      var numInvalid = 0
      combinedQuestions.forEach((question, index) => {
        initialShowContext[index] = false
        if (!question.is_valid) {
          initialReasons[index] = question.reason
          numInvalid += 1;
        }
        else {
          numValid += 1;
        }
      });
      setShowContext(initialShowContext)
      setStats({'valid': numValid, 'invalid': numInvalid, 'total': numValid + numInvalid})
      setReasons(initialReasons);
    }
    else {
      setStats({'valid': 0, 'invalid': 0, 'total': combinedQuestions.length})
    }
    // console.log("COMBINED QUESTIONS", combinedQuestions);
  };

  if (!currentUser) {
    return (<PromptLogin />);
  }

  const DefaultWordHighlighter = ({masked_statement, term, index}) => {
    const words = masked_statement.split(" ");
    const maskIndex = words.indexOf('<MASK>');
    const sentence = masked_statement.replace('<MASK>', term);
  
    const handleTermChange = async (newSentence, newTerm) => {
      if (newSentence != validations[index].statement && window.confirm("Are you sure you want to change the term?")) {
        const updatedValidations = validations.map((item, i) => {
          if (i === index) {
            return { ...item, statement: newSentence, term: newTerm };
          }
          return item;
        });
        setValidations(updatedValidations);
  
        const question = updatedValidations[index];
        // console.log(question)
        await apiClient.updateClozeQuestion(
          question.id,
          question.statement,
          question.term
        );
      }
    };
  
    return (
      <WordHighlighterUpdate
        sentence={sentence}
        onWordSelect={handleTermChange}
        selected={maskIndex}
      />
    );
  };

  const ContextComponent = ({index, item}) => {
    return (
      <>
      <button
        className={`validation-button ${showContext[index] ? 'selected' : ''}`}
        onClick={() => handleContextChange(index, item)}
      >
        {showContext[index] ? 'Hide Context' : 'Show Context'}
      </button>
    {showContext[index] ?
    <div className='scroll-container' 
      style={{backgroundColor:'#f9f9f9', overflowY:'unset', maxHeight:'100%'}}>
      <div className='context'>
      {contextObjs[index].context ? 
        <p><strong>Context: </strong>{contextObjs[index].context.content}
          <br/>
          <br/>
          <strong>Source:</strong> <a href={contextObjs[index].context.link}>{contextObjs[index].context.source}</a>
          <br/>
          <strong>Page:</strong> {contextObjs[index].context.page}
        </p> 
      : 
        <p>Context Unavailable</p>}
    </div>

      {contextObjs[index].retrieved_contexts ?
        contextObjs[index].retrieved_contexts.map((context, index) => (
          <div className='context retrieved'>
            {context ?
            <p><strong>Retrieved Context: </strong>{context.content}
            <br/>
            <br/>
            <strong>Source:</strong> <a href={context.link}>{context.source}</a>
            <br/>
            <strong>Page:</strong> {context.page}
          </p>
          :
          <p>Context Unavailable</p>}
          </div>
        ))
      :
          <></>
      }
    </div>
    :
    <></>
    }
    </>
    )
  }

  // console.log(questionType)

  return (
    <div className="AnsweredQuestions">
      <h1>Validated Questions</h1>
      <div style={{display:'flex'}}>
          <div style = {{margin:'10px', fontSize:'20px', marginTop:'5px'}}>
          <select id="question_type" name="question_type" onChange={handleDropdownChange}>
            <option value="MCQ">MCQ</option>
            <option value="FREE_FORM">Free Form</option>
            <option value="CLOZE">Cloze</option>
          </select>
        </div>
        <div style = {{margin:'10px', fontSize:'20px', marginTop:'5px'}}>
          Valid: <span style={{color: 'green'}}> {stats.valid} </span>
        </div>
        <div style = {{margin:'10px', fontSize:'20px', marginTop:'5px'}}>
          Invalid: <span style={{color: 'red'}}>{stats.invalid} </span>
        </div>
        <div style = {{margin:'10px', fontSize:'20px', marginTop:'5px'}}>
          Total: {stats.total}
        </div>
      </div>
      <hr/>
      <div style={{overflowY:'scroll', maxHeight:'700px'}}>
      {validations.length === 0 ? (
        <p>No questions have been answered yet.</p>
      ) : (
        <ul>
          {questionType != "CLOZE" && validations.map((item, index) => (
            <li key={index}>
              <p><strong>Question:</strong> {item.question}</p>
              {/* <p><strong>Context:</strong> {item.context}</p> */}
              {item.question_type === 'MCQ' ? (
                <div>
                  {/* <p><strong>Options:</strong></p> */}
                  <ul>
                    {Object.entries(item.options).map(([key, value]) => (
                      <li key={key} className={key === item.correct_option ? 'correct-answer' : ''}>
                        {value} {key === item.correct_option && <span className="checkmark">✔</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <div>
                  <p><strong>Answer:</strong> {item.answer}</p>
                </div>
              )}
              <p><strong>Complexity:</strong> {item.question_complexity}</p>
              <br/>
              <p><strong>User:</strong> {item.user_email}</p>
              <p><strong>Opened:</strong> {new Date(item.open_timestamp).toLocaleString('en-US')}</p>
              <p><strong>Submitted:</strong> {new Date(item.submission_timestamp).toLocaleString('en-US')}</p>
              <br/>
              <p>
                <strong>Validation:</strong>
                <button
                  className={`validation-button ${item.is_valid? 'selected' : ''}`}
                  onClick={() => handleValidationChange(index, true)}
                >
                  Valid
                </button>
                <button
                  className={`validation-button ${!item.is_valid? 'selected' : ''}`}
                  onClick={() => handleValidationChange(index, false)}
                >
                  Invalid
                </button>
              </p>
              {!item.is_valid && (
              <div style={{display:'flex'}}>
                 <p><strong>Invalidity Reason:</strong></p>
                 <textarea
                    style={{width:'85%', height:'20px', marginLeft:'10px'}}
                    value={reasons[index]}
                    onChange={(e) => handleReasonChange(index, e.target.value)}
                    onBlur={() => handleReasonBlur(index)}
                    placeholder='Please specify the reason...'
                  />
              </div>
              )}
              <br/>
              <ContextComponent index={index} item={item} />
            </li>
          ))}
          {questionType == "CLOZE" && validations.map((item, index) => (
              <li key={index}>
                { item.question_type === "CLOZE" ?
                    <DefaultWordHighlighter masked_statement={item.statement} term={item.term} index={index} />
                  :
                    <></>
                }
                 <br/>
                <p><strong>User:</strong> {item.user_email}</p>
                <p><strong>Opened:</strong> {new Date(item.open_timestamp).toLocaleString('en-US')}</p>
              <p><strong>Submitted:</strong> {new Date(item.submission_timestamp).toLocaleString('en-US')}</p>
                <br/>
                <ContextComponent index={index} item={item} />
              </li>
            ))
          }
        </ul>
      )}
      </div>
    </div>
  );
};

export default AnsweredQuestions;
