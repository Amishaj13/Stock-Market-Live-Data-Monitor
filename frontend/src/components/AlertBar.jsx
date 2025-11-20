import React, { useState, useEffect } from 'react';
import { FiBell, FiX } from 'react-icons/fi';
import websocketService from '../services/websocket';

const AlertBar = () => {
    const [alerts, setAlerts] = useState([]);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Subscribe to alert notifications
        const handleAlert = (data) => {
            if (data.type === 'alert' || data.type === 'rule_alert') {
                const newAlert = {
                    id: Date.now(),
                    ...data.data,
                    timestamp: new Date()
                };
                setAlerts(prev => [newAlert, ...prev].slice(0, 5)); // Keep last 5 alerts
                setIsVisible(true);

                // Auto-hide after 10 seconds
                setTimeout(() => {
                    setAlerts(prev => prev.filter(a => a.id !== newAlert.id));
                }, 10000);
            }
        };

        websocketService.subscribe('alert', handleAlert);
        websocketService.subscribe('rule_alert', handleAlert);

        return () => {
            websocketService.unsubscribe('alert', handleAlert);
            websocketService.unsubscribe('rule_alert', handleAlert);
        };
    }, []);

    const removeAlert = (id) => {
        setAlerts(prev => prev.filter(alert => alert.id !== id));
    };

    if (!isVisible || alerts.length === 0) {
        return null;
    }

    return (
        <div className="fixed top-20 right-4 z-50 space-y-2 max-w-md">
            {alerts.map(alert => (
                <div
                    key={alert.id}
                    className="bg-white dark:bg-gray-800 rounded-lg shadow-xl border-l-4 border-warning p-4 animate-slideIn"
                >
                    <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0">
                                <FiBell className="w-5 h-5 text-warning" />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                                    {alert.symbol} Alert
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                                    {alert.message}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    {alert.timestamp.toLocaleTimeString()}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => removeAlert(alert.id)}
                            className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                        >
                            <FiX className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default AlertBar;
