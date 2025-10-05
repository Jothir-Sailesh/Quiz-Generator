import React, { useState, useEffect } from 'react';
import { useQuiz } from '../../contexts/QuizContext';
import { analyticsAPI } from '../../services/api';
import { TrendingUp, Target, Clock, BookOpen, BarChart3 } from 'lucide-react';

const Analytics: React.FC = () => {
  const { quizStats } = useQuiz();
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        // In a real implementation, you would fetch actual analytics data
        // For now, we'll use mock data
        setAnalyticsData({
          userStats: {
            totalQuizzes: 12,
            averageScore: 78,
            totalTime: 4.5,
            questionsAnswered: 156
          },
          performanceTrends: [
            { date: '2024-01-01', score: 65 },
            { date: '2024-01-02', score: 72 },
            { date: '2024-01-03', score: 78 },
            { date: '2024-01-04', score: 81 },
            { date: '2024-01-05', score: 85 }
          ],
          difficultyAnalysis: {
            beginner: { correct: 45, total: 50, percentage: 90 },
            intermediate: { correct: 32, total: 45, percentage: 71 },
            advanced: { correct: 18, total: 30, percentage: 60 },
            expert: { correct: 12, total: 20, percentage: 60 }
          }
        });
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const StatCard = ({ icon: Icon, title, value, change, color }: any) => (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change > 0 ? '+' : ''}{change}% from last week
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );

  const DifficultyBar = ({ level, data, color }: any) => (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${color}`}></div>
        <span className="font-medium capitalize">{level}</span>
      </div>
      <div className="flex items-center space-x-4">
        <div className="text-sm text-gray-600">
          {data.correct}/{data.total} correct
        </div>
        <div className="w-32 bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${color}`}
            style={{ width: `${data.percentage}%` }}
          />
        </div>
        <div className="text-sm font-semibold text-gray-900 w-12 text-right">
          {data.percentage}%
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold gradient-text mb-2">
          Performance Analytics
        </h1>
        <p className="text-gray-600">
          Track your learning progress and identify areas for improvement
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={BookOpen}
          title="Quizzes Completed"
          value={analyticsData?.userStats?.totalQuizzes || 0}
          change={12}
          color="bg-blue-500"
        />
        <StatCard
          icon={Target}
          title="Average Score"
          value={`${analyticsData?.userStats?.averageScore || 0}%`}
          change={5}
          color="bg-green-500"
        />
        <StatCard
          icon={TrendingUp}
          title="Questions Answered"
          value={analyticsData?.userStats?.questionsAnswered || 0}
          change={8}
          color="bg-purple-500"
        />
        <StatCard
          icon={Clock}
          title="Study Time"
          value={`${analyticsData?.userStats?.totalTime || 0}h`}
          change={15}
          color="bg-orange-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Performance by Difficulty */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <BarChart3 className="h-6 w-6 mr-2" />
            Performance by Difficulty
          </h2>
          <div className="space-y-4">
            <DifficultyBar
              level="beginner"
              data={analyticsData?.difficultyAnalysis?.beginner}
              color="bg-green-500"
            />
            <DifficultyBar
              level="intermediate"
              data={analyticsData?.difficultyAnalysis?.intermediate}
              color="bg-yellow-500"
            />
            <DifficultyBar
              level="advanced"
              data={analyticsData?.difficultyAnalysis?.advanced}
              color="bg-red-500"
            />
            <DifficultyBar
              level="expert"
              data={analyticsData?.difficultyAnalysis?.expert}
              color="bg-purple-500"
            />
          </div>
        </div>

        {/* Recent Quiz Stats */}
        {quizStats && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Latest Quiz Results
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Questions</span>
                <span className="font-semibold">{quizStats.total_questions}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Correct Answers</span>
                <span className="font-semibold text-green-600">
                  {quizStats.correct_answers}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Incorrect Answers</span>
                <span className="font-semibold text-red-600">
                  {quizStats.incorrect_answers}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Accuracy</span>
                <span className="font-semibold">
                  {(quizStats.accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg. Time per Question</span>
                <span className="font-semibold">
                  {quizStats.average_time_per_question?.toFixed(1)}s
                </span>
              </div>
            </div>

            {/* Accuracy Visualization */}
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Accuracy</span>
                <span>{(quizStats.accuracy * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full"
                  style={{ width: `${quizStats.accuracy * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Performance Insights */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Performance Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
            <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-semibold text-green-800">Strengths</h3>
            <p className="text-sm text-green-700 mt-1">
              Excellent performance on beginner-level questions. Keep it up!
            </p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <Target className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold text-yellow-800">Areas to Focus</h3>
            <p className="text-sm text-yellow-700 mt-1">
              Advanced topics need more practice. Consider reviewing study materials.
            </p>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
            <Clock className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-semibold text-blue-800">Speed</h3>
            <p className="text-sm text-blue-700 mt-1">
              Good pacing overall. Try to maintain consistency across all difficulty levels.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;