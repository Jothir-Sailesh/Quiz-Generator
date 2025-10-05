import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { quizAPI } from '../../services/api';
import { Plus, BookOpen, Target, TrendingUp, Clock } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [treeStructure, setTreeStructure] = useState<any>(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [stats, setStats] = useState({
    totalQuizzes: 0,
    averageScore: 0,
    totalQuestions: 0,
    studyTime: 0
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const treeData = await quizAPI.getTreeStructure();
        setTreeStructure(treeData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      }
    };

    fetchDashboardData();
  }, []);

  const StatCard = ({ icon: Icon, title, value, color }: any) => (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.full_name || user?.username}! 👋
        </h1>
        <p className="text-lg text-gray-600">
          Ready to test your knowledge with AI-generated quizzes?
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={BookOpen}
          title="Total Quizzes"
          value={stats.totalQuizzes}
          color="bg-blue-500"
        />
        <StatCard
          icon={Target}
          title="Average Score"
          value={`${stats.averageScore}%`}
          color="bg-green-500"
        />
        <StatCard
          icon={TrendingUp}
          title="Questions Answered"
          value={stats.totalQuestions}
          color="bg-purple-500"
        />
        <StatCard
          icon={Clock}
          title="Study Time"
          value={`${stats.studyTime}h`}
          color="bg-orange-500"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="space-y-4">
            <Link
              to="/create-quiz"
              className="flex items-center justify-between p-4 border-2 border-dashed border-blue-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <Plus className="h-6 w-6 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-gray-900">Create New Quiz</h3>
                  <p className="text-sm text-gray-600">
                    Generate questions from your text content
                  </p>
                </div>
              </div>
              <div className="text-blue-600 group-hover:translate-x-1 transition-transform">
                →
              </div>
            </Link>

            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">How it works:</h3>
              <ol className="text-sm text-gray-600 space-y-1">
                <li>1. Upload your study material or lecture notes</li>
                <li>2. AI generates personalized quiz questions</li>
                <li>3. Take the quiz with adaptive difficulty</li>
                <li>4. Get instant feedback and track progress</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Question Tree Overview */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Knowledge Areas
          </h2>
          {treeStructure ? (
            <div className="space-y-3">
              <div className="text-sm text-gray-600 mb-3">
                Total Questions: {treeStructure.statistics?.total_questions || 0}
              </div>
              {Object.entries(treeStructure.statistics?.subjects_detail || {}).map(([subject, data]: [string, any]) => (
                <div key={subject} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-center">
                    <h4 className="font-medium text-gray-900 capitalize">{subject}</h4>
                    <span className="text-sm text-gray-600">
                      {data.total_questions} questions
                    </span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {Object.keys(data.topics_detail || {}).map((topic) => (
                      <span
                        key={topic}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
              {Object.keys(treeStructure.statistics?.subjects_detail || {}).length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <BookOpen className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No quizzes created yet</p>
                  <p className="text-sm">Create your first quiz to get started!</p>
                </div>
              )}
            </div>
          ) : (
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-3"></div>
              <div className="h-8 bg-gray-200 rounded mb-2"></div>
              <div className="h-8 bg-gray-200 rounded mb-2"></div>
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          )}
        </div>
      </div>

      {/* Features Overview */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Platform Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
              <BookOpen className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-semibold">AI-Generated Questions</h3>
            <p className="text-sm text-gray-600">
              Automatically create quiz questions from any text content using advanced AI
            </p>
          </div>
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <Target className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-semibold">Adaptive Difficulty</h3>
            <p className="text-sm text-gray-600">
              Dynamic difficulty adjustment based on your performance using machine learning
            </p>
          </div>
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-semibold">Performance Analytics</h3>
            <p className="text-sm text-gray-600">
              Track your progress and identify areas for improvement with detailed analytics
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;