"""
Watchlist Routes
Handles watchlist CRUD operations
"""

from flask import Blueprint, request, jsonify
from models import db, Watchlist
from middleware import token_required
import logging

logger = logging.getLogger(__name__)

watchlist_bp = Blueprint('watchlist', __name__)


@watchlist_bp.route('', methods=['GET'])
@token_required
def get_watchlist(current_user):
    """Get user's watchlist"""
    try:
        watchlist_items = Watchlist.query.filter_by(user_id=current_user.id).all()
        
        return jsonify({
            'status': 'success',
            'count': len(watchlist_items),
            'watchlist': [item.to_dict() for item in watchlist_items]
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching watchlist: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@watchlist_bp.route('', methods=['POST'])
@token_required
def add_to_watchlist(current_user):
    """Add stock to watchlist"""
    try:
        data = request.get_json()
        
        if 'symbol' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Symbol is required'
            }), 400
        
        symbol = data['symbol'].upper()
        
        # Check if already in watchlist
        existing = Watchlist.query.filter_by(
            user_id=current_user.id,
            symbol=symbol
        ).first()
        
        if existing:
            return jsonify({
                'status': 'error',
                'message': 'Stock already in watchlist'
            }), 409
        
        # Add to watchlist
        watchlist_item = Watchlist(
            user_id=current_user.id,
            symbol=symbol
        )
        
        db.session.add(watchlist_item)
        db.session.commit()
        
        logger.info(f"Added {symbol} to watchlist for user {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Stock added to watchlist',
            'item': watchlist_item.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@watchlist_bp.route('/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_watchlist(current_user, item_id):
    """Remove stock from watchlist"""
    try:
        watchlist_item = Watchlist.query.filter_by(
            id=item_id,
            user_id=current_user.id
        ).first()
        
        if not watchlist_item:
            return jsonify({
                'status': 'error',
                'message': 'Watchlist item not found'
            }), 404
        
        symbol = watchlist_item.symbol
        db.session.delete(watchlist_item)
        db.session.commit()
        
        logger.info(f"Removed {symbol} from watchlist for user {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Stock removed from watchlist'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@watchlist_bp.route('/symbol/<symbol>', methods=['DELETE'])
@token_required
def remove_by_symbol(current_user, symbol):
    """Remove stock from watchlist by symbol"""
    try:
        watchlist_item = Watchlist.query.filter_by(
            user_id=current_user.id,
            symbol=symbol.upper()
        ).first()
        
        if not watchlist_item:
            return jsonify({
                'status': 'error',
                'message': 'Stock not in watchlist'
            }), 404
        
        db.session.delete(watchlist_item)
        db.session.commit()
        
        logger.info(f"Removed {symbol} from watchlist for user {current_user.id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Stock removed from watchlist'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@watchlist_bp.route('/check/<symbol>', methods=['GET'])
@token_required
def check_in_watchlist(current_user, symbol):
    """Check if stock is in watchlist"""
    try:
        exists = Watchlist.query.filter_by(
            user_id=current_user.id,
            symbol=symbol.upper()
        ).first() is not None
        
        return jsonify({
            'status': 'success',
            'symbol': symbol.upper(),
            'in_watchlist': exists
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking watchlist: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
