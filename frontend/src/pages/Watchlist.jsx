import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import StockCard from '../components/StockCard';
import { watchlistAPI } from '../services/api';
import { FiPlus, FiSearch } from 'react-icons/fi';

const Watchlist = () => {
    const [watchlist, setWatchlist] = useState([]);
    const [loading, setLoading] = useState(true);
    const [addingStock, setAddingStock] = useState(false);
    const [newSymbol, setNewSymbol] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchWatchlist();
    }, []);

    const fetchWatchlist = async () => {
        try {
            setLoading(true);
            const response = await watchlistAPI.getWatchlist();

            if (response.data.status === 'success') {
                setWatchlist(response.data.watchlist);
            }
        } catch (err) {
            setError('Failed to load watchlist');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddStock = async (e) => {
        e.preventDefault();
        setError('');

        if (!newSymbol.trim()) {
            setError('Please enter a stock symbol');
            return;
        }

        try {
            const response = await watchlistAPI.addToWatchlist(newSymbol.toUpperCase());

            if (response.data.status === 'success') {
                setNewSymbol('');
                setAddingStock(false);
                fetchWatchlist(); // Refresh watchlist
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to add stock');
        }
    };

    const handleRemoveStock = async (stock) => {
        try {
            await watchlistAPI.removeFromWatchlist(stock.id);
            fetchWatchlist(); // Refresh watchlist
        } catch (err) {
            setError('Failed to remove stock');
            console.error(err);
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

    return (
        <>
            <Navbar />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            My Watchlist
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-1">
                            Manage your tracked stocks
                        </p>
                    </div>

                    <button
                        onClick={() => setAddingStock(!addingStock)}
                        className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                    >
                        <FiPlus className="w-5 h-5" />
                        <span>Add Stock</span>
                    </button>
                </div>

                {/* Add stock form */}
                {addingStock && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-8">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                            Add Stock to Watchlist
                        </h3>

                        {error && (
                            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleAddStock} className="flex space-x-4">
                            <div className="flex-1 relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <FiSearch className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    value={newSymbol}
                                    onChange={(e) => setNewSymbol(e.target.value)}
                                    placeholder="Enter stock symbol (e.g., AAPL)"
                                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                            <button
                                type="submit"
                                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                            >
                                Add
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setAddingStock(false);
                                    setNewSymbol('');
                                    setError('');
                                }}
                                className="px-6 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                            >
                                Cancel
                            </button>
                        </form>
                    </div>
                )}

                {/* Watchlist grid */}
                {watchlist.length === 0 ? (
                    <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                        <div className="text-6xl mb-4">📊</div>
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            Your watchlist is empty
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400 mb-6">
                            Start tracking stocks by adding them to your watchlist
                        </p>
                        <button
                            onClick={() => setAddingStock(true)}
                            className="inline-flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                        >
                            <FiPlus className="w-5 h-5" />
                            <span>Add Your First Stock</span>
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {watchlist.map(item => (
                            <StockCard
                                key={item.id}
                                stock={{ symbol: item.symbol, ...item }}
                                showActions={true}
                                onRemove={handleRemoveStock}
                            />
                        ))}
                    </div>
                )}
            </div>
        </>
    );
};

export default Watchlist;
