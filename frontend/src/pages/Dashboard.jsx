import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import StockCard from '../components/StockCard';
import AlertBar from '../components/AlertBar';
import { stockAPI } from '../services/api';
import websocketService from '../services/websocket';
import { FiRefreshCw, FiTrendingUp, FiTrendingDown } from 'react-icons/fi';

const Dashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [wsConnected, setWsConnected] = useState(false);

    useEffect(() => {
        fetchDashboardData();

        // Connect to WebSocket
        websocketService.connect();

        // Subscribe to connection status
        websocketService.subscribe('connection', (data) => {
            setWsConnected(data.status === 'connected');
        });

        // Subscribe to stock updates
        websocketService.subscribe('stock_update', (data) => {
            // Update stock data in real-time
            updateStockData(data);
        });

        return () => {
            websocketService.disconnect();
        };
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const response = await stockAPI.getDashboard();

            if (response.data.status === 'success') {
                setDashboardData(response.data.data);
            }
        } catch (err) {
            setError('Failed to load dashboard data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const updateStockData = (updatedStock) => {
        if (!dashboardData) return;

        setDashboardData(prev => ({
            ...prev,
            stocks: prev.stocks.map(stock =>
                stock.symbol === updatedStock.symbol ? { ...stock, ...updatedStock } : stock
            )
        }));
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

    const { stocks = [], summary = {} } = dashboardData || {};

    return (
        <>
            <Navbar />
            <AlertBar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            Dashboard
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-1">
                            Real-time stock market monitoring
                        </p>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* WebSocket status */}
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-success animate-pulse' : 'bg-gray-400'}`}></div>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                {wsConnected ? 'Live' : 'Disconnected'}
                            </span>
                        </div>

                        {/* Refresh button */}
                        <button
                            onClick={fetchDashboardData}
                            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                        >
                            <FiRefreshCw className="w-4 h-4" />
                            <span>Refresh</span>
                        </button>
                    </div>
                </div>

                {/* Summary cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Total Stocks</p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                                    {summary.total_stocks || 0}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">📊</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Gainers</p>
                                <p className="text-3xl font-bold text-success mt-2">
                                    {summary.gainers || 0}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                                <FiTrendingUp className="w-6 h-6 text-success" />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">Losers</p>
                                <p className="text-3xl font-bold text-danger mt-2">
                                    {summary.losers || 0}
                                </p>
                            </div>
                            <div className="w-12 h-12 bg-red-100 dark:bg-red-900 rounded-lg flex items-center justify-center">
                                <FiTrendingDown className="w-6 h-6 text-danger" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Stock grid */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-400">
                        {error}
                    </div>
                )}

                {stocks.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-600 dark:text-gray-400 text-lg">
                            No stocks in your watchlist. Add some to get started!
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {stocks.map(stock => (
                            <StockCard key={stock.symbol} stock={stock} showActions={false} />
                        ))}
                    </div>
                )}
            </div>
        </>
    );
};

export default Dashboard;
