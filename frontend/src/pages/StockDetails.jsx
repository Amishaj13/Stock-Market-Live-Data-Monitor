import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import StockChart from '../components/StockChart';
import { stockAPI } from '../services/api';
import { FiArrowLeft, FiTrendingUp, FiTrendingDown, FiActivity } from 'react-icons/fi';

const StockDetails = () => {
    const { symbol } = useParams();
    const navigate = useNavigate();
    const [stockData, setStockData] = useState(null);
    const [history, setHistory] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchStockDetails();
    }, [symbol]);

    const fetchStockDetails = async () => {
        try {
            setLoading(true);

            // Fetch latest data
            const latestResponse = await stockAPI.getLatest(symbol);
            if (latestResponse.data.status === 'success') {
                setStockData(latestResponse.data.data);
            }

            // Fetch history
            const historyResponse = await stockAPI.getHistory(symbol, { limit: 50 });
            if (historyResponse.data.status === 'success') {
                setHistory(historyResponse.data.data);
            }

            // Fetch analytics
            const analyticsResponse = await stockAPI.getAnalytics(symbol);
            if (analyticsResponse.data.status === 'success') {
                setAnalytics(analyticsResponse.data.analytics);
            }

        } catch (err) {
            setError('Failed to load stock details');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <>
                <Navbar />
                <div className="flex items-center justify-center min-h-screen">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
            </>
        );
    }

    if (error || !stockData) {
        return (
            <>
                <Navbar />
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="text-center py-12">
                        <p className="text-red-600 text-lg">{error || 'Stock not found'}</p>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                        >
                            Back to Dashboard
                        </button>
                    </div>
                </div>
            </>
        );
    }

    const isPositive = stockData.change_percent >= 0;

    return (
        <>
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Back button */}
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6"
                >
                    <FiArrowLeft className="w-5 h-5" />
                    <span>Back</span>
                </button>

                {/* Stock header */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 mb-6">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                                {symbol}
                            </h1>
                            <p className="text-gray-600 dark:text-gray-400">
                                Volume: {stockData.volume?.toLocaleString() || 'N/A'}
                            </p>
                        </div>

                        <div className="text-right">
                            <p className="text-4xl font-bold text-gray-900 dark:text-white">
                                ${stockData.price.toFixed(2)}
                            </p>
                            <div className={`flex items-center justify-end space-x-2 mt-2 ${isPositive ? 'text-success' : 'text-danger'}`}>
                                {isPositive ? <FiTrendingUp className="w-6 h-6" /> : <FiTrendingDown className="w-6 h-6" />}
                                <span className="text-xl font-semibold">
                                    {isPositive ? '+' : ''}{stockData.change?.toFixed(2)} ({isPositive ? '+' : ''}{stockData.change_percent?.toFixed(2)}%)
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Analytics cards */}
                {analytics && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-2">
                                <FiActivity className="w-5 h-5" />
                                <span className="text-sm">Average Price</span>
                            </div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                ${analytics.avg_price?.toFixed(2) || 'N/A'}
                            </p>
                        </div>

                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                            <div className="flex items-center space-x-2 text-success mb-2">
                                <FiTrendingUp className="w-5 h-5" />
                                <span className="text-sm">High</span>
                            </div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                ${analytics.max_price?.toFixed(2) || 'N/A'}
                            </p>
                        </div>

                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                            <div className="flex items-center space-x-2 text-danger mb-2">
                                <FiTrendingDown className="w-5 h-5" />
                                <span className="text-sm">Low</span>
                            </div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                ${analytics.min_price?.toFixed(2) || 'N/A'}
                            </p>
                        </div>

                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 mb-2">
                                <span className="text-sm">Trend</span>
                            </div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                {analytics.trend_direction || 'N/A'}
                            </p>
                        </div>
                    </div>
                )}

                {/* Price chart */}
                <StockChart data={history} symbol={symbol} />
            </div>
        </>
    );
};

export default StockDetails;
