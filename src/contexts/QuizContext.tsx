import React, { createContext, useContext, useState, ReactNode } from 'react';
import { quizAPI } from '../services/api';

interface Question {
  id: string;
  text: string;
  question_type: string;
  options?: Array<{ text: string }>;
  difficulty: string;
  topic: string;
  remaining_questions: number;
}

interface QuizStats {
  total_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  accuracy: number;
  average_time_per_question: number;
}

interface QuizContextType {
  currentQuiz: any | null;
  currentQuestion: Question | null;
  quizStats: QuizStats | null;
  isLoading: boolean;
  createQuiz: (quizData: any) => Promise<void>;
  getNextQuestion: (quizId: string) => Promise<void>;
  submitAnswer: (quizId: string, answerData: any) => Promise<any>;
  getQuizStats: (quizId: string) => Promise<void>;
  endQuizSession: (quizId: string) => Promise<void>;
  resetQuiz: () => void;
}

const QuizContext = createContext<QuizContextType | undefined>(undefined);

interface QuizProviderProps {
  children: ReactNode;
}

export const QuizProvider: React.FC<QuizProviderProps> = ({ children }) => {
  const [currentQuiz, setCurrentQuiz] = useState<any | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [quizStats, setQuizStats] = useState<QuizStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const createQuiz = async (quizData: any) => {
    setIsLoading(true);
    try {
      const quiz = await quizAPI.createQuiz(quizData);
      setCurrentQuiz(quiz);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getNextQuestion = async (quizId: string) => {
    setIsLoading(true);
    try {
      const response = await quizAPI.getNextQuestion(quizId);
      setCurrentQuestion(response.question);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async (quizId: string, answerData: any) => {
    try {
      const feedback = await quizAPI.submitAnswer(quizId, answerData);
      return feedback;
    } catch (error) {
      throw error;
    }
  };

  const getQuizStats = async (quizId: string) => {
    try {
      const stats = await quizAPI.getQuizStats(quizId);
      setQuizStats(stats.quiz_stats);
    } catch (error) {
      throw error;
    }
  };

  const endQuizSession = async (quizId: string) => {
    try {
      await quizAPI.endQuizSession(quizId);
      resetQuiz();
    } catch (error) {
      throw error;
    }
  };

  const resetQuiz = () => {
    setCurrentQuiz(null);
    setCurrentQuestion(null);
    setQuizStats(null);
  };

  const value = {
    currentQuiz,
    currentQuestion,
    quizStats,
    isLoading,
    createQuiz,
    getNextQuestion,
    submitAnswer,
    getQuizStats,
    endQuizSession,
    resetQuiz
  };

  return <QuizContext.Provider value={value}>{children}</QuizContext.Provider>;
};

export const useQuiz = () => {
  const context = useContext(QuizContext);
  if (context === undefined) {
    throw new Error('useQuiz must be used within a QuizProvider');
  }
  return context;
};