import { Link } from 'react-router-dom';
import { usePrivy } from '@privy-io/react-auth';
import { 
  Leaf, 
  MessageCircle, 
  Upload, 
  BarChart3, 
  Trophy,
  ArrowRight,
  CheckCircle,
  Zap,
  Shield,
  Globe
} from 'lucide-react';

export default function HomePage() {
  const { authenticated } = usePrivy();

  const features = [
    {
      icon: MessageCircle,
      title: 'AI-Powered Chat',
      description: 'Chat with our sustainability AI to get personalized recommendations and insights.',
    },
    {
      icon: Upload,
      title: 'Document Analysis',
      description: 'Upload sustainability reports and get instant carbon credit calculations.',
    },
    {
      icon: BarChart3,
      title: 'Analytics Dashboard',
      description: 'Track your sustainability progress with detailed analytics and metrics.',
    },
    {
      icon: Trophy,
      title: 'Leaderboard',
      description: 'Compete with others and see how you rank in sustainability efforts.',
    },
  ];

  const benefits = [
    'AI-powered sustainability analysis',
    'Blockchain-verified carbon credits',
    'Real-time impact tracking',
    'Community leaderboards',
    'Personalized recommendations',
    'Transparent reporting',
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-eco-600 rounded-2xl flex items-center justify-center">
            <Leaf className="w-8 h-8 text-white" />
          </div>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          Track Your
          <span className="text-eco-600"> Sustainability</span>
          <br />
          Journey
        </h1>
        
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          EcoChain uses AI and blockchain technology to help you track, verify, and monetize your sustainability efforts. 
          Get rewarded for making a positive environmental impact.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {authenticated ? (
            <>
              <Link to="/upload" className="btn-primary text-lg px-8 py-3">
                Upload Document
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
              <Link to="/dashboard" className="btn-secondary text-lg px-8 py-3">
                View Dashboard
              </Link>
            </>
          ) : (
            <>
              <Link to="/chat" className="btn-primary text-lg px-8 py-3">
                Start Chatting
                <MessageCircle className="w-5 h-5 ml-2" />
              </Link>
              <Link to="/upload" className="btn-secondary text-lg px-8 py-3">
                Try Upload
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div key={index} className="card text-center hover:shadow-lg transition-shadow duration-200">
              <div className="w-12 h-12 bg-eco-100 dark:bg-eco-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Icon className="w-6 h-6 text-eco-600 dark:text-eco-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {feature.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Benefits Section */}
      <div className="bg-eco-50 dark:bg-eco-900/10 rounded-2xl p-8 md:p-12">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Why Choose EcoChain?
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Join thousands of users making a real impact on the environment
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {benefits.map((benefit, index) => (
            <div key={index} className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-eco-600 dark:text-eco-400 flex-shrink-0" />
              <span className="text-gray-700 dark:text-gray-300">{benefit}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Powered by Advanced Technology
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              AI Analysis
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Advanced AI powered by MeTTa for accurate sustainability analysis
            </p>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Shield className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Blockchain Security
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Secure, transparent, and immutable record of your sustainability efforts
            </p>
          </div>

          <div className="card text-center">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center mx-auto mb-4">
              <Globe className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Global Impact
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Join a global community working towards a sustainable future
            </p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center bg-gray-900 dark:bg-gray-800 rounded-2xl p-8 md:p-12 text-white">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Make a Difference?
        </h2>
        <p className="text-xl text-gray-300 mb-8">
          Start your sustainability journey today and earn rewards for your environmental impact.
        </p>
        <Link to="/upload" className="btn-primary text-lg px-8 py-3 bg-eco-600 hover:bg-eco-700">
          Get Started Now
          <ArrowRight className="w-5 h-5 ml-2" />
        </Link>
      </div>
    </div>
  );
}
