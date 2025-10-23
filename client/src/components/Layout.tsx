import { type ReactNode, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { usePrivy } from '@privy-io/react-auth';
import { 
  Home, 
  MessageCircle, 
  Upload, 
  BarChart3, 
  Trophy,
  Menu,
  X,
  Sun,
  Moon,
  Wallet
} from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { ready, authenticated, user, login, logout } = usePrivy();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const location = useLocation();

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Chat', href: '/chat', icon: MessageCircle },
    { name: 'Upload', href: '/upload', icon: Upload },
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Leaderboard', href: '/leaderboard', icon: Trophy },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navbar */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo and navigation */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-eco-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">E</span>
                </div>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  EcoChain
                </span>
              </Link>

              {/* Desktop navigation */}
              <div className="hidden md:ml-8 md:flex md:space-x-8">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`inline-flex items-center px-1 pt-1 text-sm font-medium border-b-2 transition-colors duration-200 ${
                        isActive(item.href)
                          ? 'border-eco-500 text-eco-600 dark:text-eco-400'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                      }`}
                    >
                      <Icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              {/* Dark mode toggle */}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* Wallet connection */}
              {ready && (
                <div className="flex items-center space-x-2">
                  {authenticated ? (
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-2 px-3 py-2 bg-eco-50 dark:bg-eco-900/20 rounded-lg">
                        <Wallet className="w-4 h-4 text-eco-600 dark:text-eco-400" />
                        <span className="text-sm font-medium text-eco-700 dark:text-eco-300">
                          {user?.wallet?.address ? 
                            `${user.wallet.address.slice(0, 6)}...${user.wallet.address.slice(-4)}` : 
                            'Connected'
                          }
                        </span>
                      </div>
                      <button
                        onClick={logout}
                        className="btn-secondary text-sm"
                      >
                        Disconnect
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={login}
                      className="btn-primary text-sm"
                    >
                      Connect Wallet
                    </button>
                  )}
                </div>
              )}

              {/* Mobile menu button */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsMenuOpen(false)}
                    className={`flex items-center px-3 py-2 text-base font-medium rounded-lg transition-colors duration-200 ${
                      isActive(item.href)
                        ? 'bg-eco-50 text-eco-600 dark:bg-eco-900/20 dark:text-eco-400'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
