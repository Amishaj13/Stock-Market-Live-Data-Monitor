import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FiTrendingUp, FiTrendingDown } from 'react-icons/fi';

const StockCard = ({ stock, showActions = true, onRemove }) => {
    const navigate = useNavigate();

    const {
        symbol,
        price = 0,
        change = 0,
        change_percent = 0,
        volume = 0,
        trend = 'NEUTRAL'
    } = stock;

    const isPositive = change_percent >= 0;

    const handleClick = () => {
        navigate(`/stock/${symbol}`);
    };

    return (
        <div
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden"
            onClick={handleClick}
        >
            <div className="p-6">
                {/* Header */}
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                            {symbol}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Vol: {volume.toLocaleString()}
                        </p>
                    </div>
                    <div className={`flex items-center space-x-1 ${isPositive ? 'text-success' : 'text-danger'}`}>
                        {isPositive ? (
                            <FiTrendingUp className="w-6 h-6" />
                        ) : (
                            <FiTrendingDown className="w-6 h-6" />
                        )}
                    </div>
                </div>

                {/* Price */}
                <div className="mb-4">
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                        ${price.toFixed(2)}
                    </p>
                </div>

                {/* Change */}
                <div className="flex items-center justify-between">
                    <div className={`flex items-center space-x-2 ${isPositive ? 'text-success' : 'text-danger'}`}>
                        <span className="text-lg font-semibold">
                            {isPositive ? '+' : ''}{change.toFixed(2)}
                        </span>
                        <span className="text-sm">
                            ({isPositive ? '+' : ''}{change_percent.toFixed(2)}%)
                        </span>
                    </div>

                    {/* Trend badge */}
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${trend === 'UP' ? 'bg-success/20 text-success' :
                            trend === 'DOWN' ? 'bg-danger/20 text-danger' :
                                'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                        }`}>
                        {trend}
                    </span>
                </div>

                {/* Remove button */}
                {showActions && onRemove && (
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onRemove(stock);
                        }}
                        className="mt-4 w-full px-4 py-2 text-sm font-medium text-red-600 bg-red-50 dark:bg-red-900/20 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                    >
                        Remove from Watchlist
                    </button>
                )}
            </div>

            {/* Animated border */}
            <div className={`h-1 ${isPositive ? 'bg-success' : 'bg-danger'}`}></div>
        </div>
    );
};

export default StockCard;
