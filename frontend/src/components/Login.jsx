/**
 * Login Component
 * 
 * Provides user authentication interface for the HR Chatbot application.
 * Features:
 * - LDAP-based authentication
 * - Form validation and error handling
 * - Theme toggle support
 * - Test account information display
 * - Responsive design with dark mode support
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from './ThemeToggle';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(username, password);

        if (result.success) {
            navigate('/chat');
        } else {
            setError(result.error);
        }

        setLoading(false);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 dark:from-gray-900 dark:to-gray-800 p-4">
            <div className="absolute top-4 right-4">
                <ThemeToggle />
            </div>

            <div className="card w-full max-w-md p-8 animate-fade-in">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-[var(--color-text-primary)] mb-2">
                        Chatbot RH
                    </h1>
                    <p className="text-[var(--color-text-secondary)]">
                        Connectez-vous pour accéder à l'assistant RH
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label
                            htmlFor="username"
                            className="block text-sm font-medium text-[var(--color-text-primary)] mb-2"
                        >
                            Nom d'utilisateur
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="input-field"
                            placeholder="Entrez votre nom d'utilisateur"
                            required
                            autoFocus
                        />
                    </div>

                    <div>
                        <label
                            htmlFor="password"
                            className="block text-sm font-medium text-[var(--color-text-primary)] mb-2"
                        >
                            Mot de passe
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="input-field"
                            placeholder="Entrez votre mot de passe"
                            required
                        />
                    </div>

                    {error && (
                        <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg animate-slide-up">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full"
                    >
                        {loading ? 'Connexion...' : 'Se connecter'}
                    </button>
                </form>

                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-300 font-medium mb-2">
                        Comptes de test :
                    </p>
                    <ul className="text-xs text-blue-700 dark:text-blue-400 space-y-1">
                        <li>• alice / password (CDI - Cadre)</li>
                        <li>• bob / password (CDD - Non-Cadre)</li>
                        <li>• charlie / password (Intérim)</li>
                        <li>• david / password (Stagiaire)</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default Login;
