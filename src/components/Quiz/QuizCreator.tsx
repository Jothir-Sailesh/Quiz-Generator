import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuiz } from '../../contexts/QuizContext';
import { Upload, FileText, Settings, Brain } from 'lucide-react';

const QuizCreator: React.FC = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    subject: '',
    sourceText: '',
    questionCount: 5,
    difficulty: ['intermediate'],
    timeLimit: null as number | null,
    adaptiveDifficulty: true,
    randomizeQuestions: true
  });
  const [apiKey, setApiKey] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const { createQuiz } = useQuiz();
  const navigate = useNavigate();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : 
               type === 'number' ? (value ? parseInt(value) : null) : value
    }));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFormData(prev => ({
          ...prev,
          sourceText: event.target?.result as string
        }));
      };
      reader.readAsText(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const quizData = {
        title: formData.title,
        description: formData.description,
        source_text: formData.sourceText,
        configuration: {
          subject: formData.subject,
          question_count: formData.questionCount,
          difficulty_levels: formData.difficulty,
          time_limit: formData.timeLimit,
          adaptive_difficulty: formData.adaptiveDifficulty,
          randomize_questions: formData.randomizeQuestions,
          randomize_options: true,
          topics: []
        }
      };

      const url = new URL('/api/quiz/generate-quiz', window.location.origin);
      if (apiKey) {
        url.searchParams.append('ai_api_key', apiKey);
      }

      const quiz = await createQuiz(quizData);
      const quizSessionId = quiz.id || quiz._id;
      if (!quizSessionId) {
        alert('Quiz session ID not found. Please try again.');
        return;
      }
      navigate('/quiz/' + quizSessionId); // Use backend's quiz/session ID
    } catch (error) {
      console.error('Failed to create quiz:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold gradient-text mb-2">
          Create AI-Powered Quiz
        </h1>
        <p className="text-gray-600">
          Transform your study material into interactive quizzes using AI
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-center mb-8">
        {[1, 2, 3].map((stepNumber) => (
          <div key={stepNumber} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                step >= stepNumber
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {stepNumber}
            </div>
            {stepNumber < 3 && (
              <div
                className={`w-16 h-1 mx-2 ${
                  step > stepNumber ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
      </div>

      <div className="card">
        {step === 1 && (
          <div className="space-y-6">
            <div className="text-center">
              <FileText className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Basic Information</h2>
              <p className="text-gray-600">Let's start with the quiz details</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quiz Title
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., Biology Chapter 5 Quiz"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Subject
                </label>
                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  className="input-field"
                  placeholder="e.g., Biology, Mathematics, History"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="input-field"
                  placeholder="Brief description of the quiz content..."
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setStep(2)}
                className="btn-primary"
                disabled={!formData.title || !formData.subject}
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div className="text-center">
              <Upload className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Upload Content</h2>
              <p className="text-gray-600">Provide the text content for question generation</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Text File (Optional)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
                  <input
                    type="file"
                    accept=".txt,.md"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-gray-400">TXT or MD files only</p>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Or paste your content directly
                </label>
                <textarea
                  name="sourceText"
                  value={formData.sourceText}
                  onChange={handleInputChange}
                  rows={8}
                  className="input-field"
                  placeholder="Paste your study material, lecture notes, or any text content here..."
                />
              </div>

              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">💡 Tips for better questions:</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Include clear definitions and explanations</li>
                  <li>• Provide context and examples</li>
                  <li>• Use structured content (headings, lists)</li>
                  <li>• Minimum 200 words recommended</li>
                </ul>
              </div>
            </div>

            <div className="flex justify-between">
              <button onClick={() => setStep(1)} className="btn-secondary">
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="btn-primary"
                disabled={!formData.sourceText.trim()}
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <div className="text-center">
              <Settings className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Quiz Configuration</h2>
              <p className="text-gray-600">Customize your quiz settings</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Questions
                </label>
                <select
                  name="questionCount"
                  value={formData.questionCount}
                  onChange={handleInputChange}
                  className="input-field"
                >
                  <option value={5}>5 Questions</option>
                  <option value={10}>10 Questions</option>
                  <option value={15}>15 Questions</option>
                  <option value={20}>20 Questions</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Difficulty
                </label>
                <select
                  name="difficulty"
                  value={formData.difficulty[0]}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    difficulty: [e.target.value]
                  }))}
                  className="input-field"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                  <option value="expert">Expert</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key (Optional)
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="input-field"
                  placeholder="sk-... (Leave empty to use mock questions)"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Provide your OpenAI API key for AI-generated questions. If not provided, sample questions will be created.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="adaptiveDifficulty"
                  name="adaptiveDifficulty"
                  checked={formData.adaptiveDifficulty}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="adaptiveDifficulty" className="ml-2 text-sm text-gray-700">
                  Enable adaptive difficulty (adjusts based on performance)
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="randomizeQuestions"
                  name="randomizeQuestions"
                  checked={formData.randomizeQuestions}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="randomizeQuestions" className="ml-2 text-sm text-gray-700">
                  Randomize question order
                </label>
              </div>
            </div>

            <div className="flex justify-between">
              <button onClick={() => setStep(2)} className="btn-secondary">
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={isGenerating}
                className="btn-primary disabled:opacity-50 flex items-center space-x-2"
              >
                {isGenerating && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
                <Brain className="h-5 w-5" />
                <span>{isGenerating ? 'Generating...' : 'Generate Quiz'}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizCreator;