export default class ApiClient {
  constructor(baseUrl = 'http://0.0.0.0:8000') {
    this.baseUrl = baseUrl;
  }

  // Get a question from the queue
  async getQuestion(questionType) {
    const response = await fetch(`${this.baseUrl}/qadata?question_type=${questionType}`);
    const data = await response.json();
    return data;
  }

  // Get the size of the queue
  async getQueueSize(questionType) {
    const response = await fetch(`${this.baseUrl}/queue_size?question_type=${questionType}`);
    const data = await response.json();
    return data.queue_size;
  }

  // Submit a new question
  async submitQuestion(question, questionType) {

    try {
      const response = await fetch(`${this.baseUrl}/qadata`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(question),
        question_type: questionType
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error Response:", errorData);  // Log the error response for debugging
        throw new Error(`Error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.id;
    } catch (error) {
      alert('There was an error while submitting question');
      console.error("Submit Question Error:", error);  // Log any errors encountered
      throw error;
    }
  }

  // Update an existing question
  async updateQuestion(questionId, isValid, questionType, reason) {
    try {
      await fetch(`${this.baseUrl}/question/${questionId}?question_type=${questionType}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ is_valid: isValid, reason: reason })
      });
    } catch (error) {
      alert('There was an error while updating the question');
      console.error("Submit Question Error:", error);  // Log any errors encountered
      throw error;
    }
  }

  async updateClozeQuestion(questionId, statement, term) {
    const response = await fetch(`${this.baseUrl}/question/${questionId}?question_type=CLOZE`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ statement: statement, term: term })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error Response:", errorData);  // Log the error response for debugging
      throw new Error(`Error: ${response.status}`);
    }
  }

  // Get questions for a specific user
  async getQuestionsForUser(userId, questionType) {
    const response = await fetch(`${this.baseUrl}/user/${userId}/questions?question_type=${questionType}`);
    const data = await response.json();
    return data.questions;
  }

  async getContexts(context_ids) {
    const response = await fetch(`${this.baseUrl}/context`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ context_ids: context_ids })
    });
    const data = await response.json();
    return data;
  }
}