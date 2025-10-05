import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuiz } from '../../contexts/QuizContext';
import { Clock, CheckCircle, XCircle, BarChart } from 'lucide-react';

const QuizSession: React.FC = () => {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();
  const { currentQuestion, getNextQuestion, submitAnswer, getQuizStats, endQuizSession, isLoading } = useQuiz();
  
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState<any>(null);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [isQuizComplete, setIsQuizComplete] = useState(false);

  useEffect(() => {
    if (quizId) {
      loadNextQuestion();
    }
  }, [quizId]);

  const loadNextQuestion = async () => {
    try {
      if (quizId) {
        await getNextQuestion(quizId);
        setSelectedAnswer('');
        setShowFeedback(false);
        setFeedback(null);
        setQuestionStartTime(Date.now());
      }
    } catch (error) {
      console.error('Failed to load next question:', error);
      setIsQuizComplete(true);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer || !quizId || !currentQuestion) return;

    const timeTaken = (Date.now() - questionStartTime) / 1000;

    try {
      const result = await submitAnswer(quizId, {
        question_id: currentQuestion.id,
        answer: selectedAnswer,
        time_taken: timeTaken
      });

      setFeedback(result);
      setShowFeedback(true);
      setQuestionsAnswered(prev => prev + 1);
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const handleNextQuestion = async () => {
    if (currentQuestion?.remaining_questions === 0) {
      setIsQuizComplete(true);
      if (quizId) {
        await getQuizStats(quizId);
      }
    } else {
      await loadNextQuestion();
    }
  };

  const handleEndQuiz = async () => {
    if (quizId) {
      await endQuizSession(quizId);
    }
    navigate('/dashboard');
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800',
      intermediate: 'bg-yellow-100 text-yellow-800',
      advanced: 'bg-red-100 text-red-800',
      expert: 'bg-purple-100 text-purple-800'
    };
    return colors[difficulty as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading question...</p>
        </div>
      </div>
    );
  }

  if (isQuizComplete) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center py-12">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Quiz Complete! 🎉
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Great job! You've completed the quiz.
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => navigate('/analytics')}
              className="btn-primary flex items-center space-x-2"
            >
              <BarChart className="h-5 w-5" />
              <span>View Analytics</span>
            </button>
            <button
              onClick={handleEndQuiz}
              className="btn-secondary"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="card text-center py-12">
          <p className="text-gray-600">No question available.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary mt-4"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!quizId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center text-red-600 text-lg font-semibold">
          Quiz session not found. Please start a new quiz.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Quiz Header */}
      <div className="card mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Quiz in Progress</h1>
            <p className="text-gray-600">
              Question {questionsAnswered + 1} • {currentQuestion.remaining_questions + 1} remaining
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getDifficultyColor(currentQuestion.difficulty)}`}>
              {currentQuestion.difficulty}
            </div>
            <span className="text-sm text-gray-500">{currentQuestion.topic}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{Math.round((questionsAnswered / (questionsAnswered + currentQuestion.remaining_questions + 1)) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full progress-bar"
              style={{
                width: `${(questionsAnswered / (questionsAnswered + currentQuestion.remaining_questions + 1)) * 100}%`
              }}
            />
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className="card question-fade-in">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {currentQuestion.text}
          </h2>
        </div>

        {/* Answer Options */}
        {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && (
          <div className="space-y-3 mb-6">
            {currentQuestion.options.map((option, index) => {
              const isSelected = selectedAnswer === option.text;
              let optionClass = 'quiz-option';
              
              if (showFeedback && feedback) {
                if (option.text === feedback.correct_option) {
                  optionClass += ' correct';
                } else if (isSelected && !feedback.is_correct) {
                  optionClass += ' incorrect';
                }
              } else if (isSelected) {
                optionClass += ' selected';
              }

              return (
                <button
                  key={index}
                  onClick={() => !showFeedback && setSelectedAnswer(option.text)}
                  disabled={showFeedback}
                  className={optionClass}
                >
                  <div className="flex items-center justify-between">
                    <span>{option.text}</span>
                    {showFeedback && option.text === feedback?.correct_option && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    {showFeedback && isSelected && !feedback?.is_correct && option.text !== feedback?.correct_option && (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* True/False Options */}
        {currentQuestion.question_type === 'true_false' && (
          <div className="grid grid-cols-2 gap-4 mb-6">
            {['true', 'false'].map((option) => {
              const isSelected = selectedAnswer === option;
              let optionClass = 'quiz-option text-center';
              
              if (showFeedback && feedback) {
                if (option === feedback.correct_answer?.toLowerCase()) {
                  optionClass += ' correct';
                } else if (isSelected && !feedback.is_correct) {
                  optionClass += ' incorrect';
                }
              } else if (isSelected) {
                optionClass += ' selected';
              }

              return (
                <button
                  key={option}
                  onClick={() => !showFeedback && setSelectedAnswer(option)}
                  disabled={showFeedback}
                  className={optionClass}
                >
                  <div className="flex items-center justify-center">
                    <span className="capitalize font-semibold">{option}</span>
                    {showFeedback && option === feedback?.correct_answer?.toLowerCase() && (
                      <CheckCircle className="h-5 w-5 text-green-500 ml-2" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}

        {/* Feedback */}
        {showFeedback && feedback && (
          <div className={`p-4 rounded-lg mb-6 ${
            feedback.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
          } border`}>
            <div className="flex items-center space-x-2 mb-2">
              {feedback.is_correct ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              <span className={`font-semibold ${
                feedback.is_correct ? 'text-green-800' : 'text-red-800'
              }`}>
                {feedback.is_correct ? 'Correct!' : 'Incorrect'}
              </span>
            </div>
            {feedback.explanation && (
              <p className="text-gray-700">{feedback.explanation}</p>
            )}
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span>{feedback.time_taken?.toFixed(1)}s</span>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-between">
          <button
            onClick={handleEndQuiz}
            className="btn-secondary"
          >
            End Quiz
          </button>
          
          {!showFeedback ? (
            <button
              onClick={handleSubmitAnswer}
              disabled={!selectedAnswer}
              className="btn-primary disabled:opacity-50"
            >
              Submit Answer
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="btn-primary"
            >
              {currentQuestion.remaining_questions === 0 ? 'Finish Quiz' : 'Next Question'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizSession;