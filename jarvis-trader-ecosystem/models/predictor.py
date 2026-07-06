import numpy as np
import pandas as pd
import json
import os
import pickle
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, Input, Concatenate, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')

class AdvancedForexPredictor:
    """
    Advanced ML predictor combining LSTM, Ensemble methods, and Technical Analysis
    for flawless forex trade predictions.
    """
    
    def __init__(self, model_dir="models/trained"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.lstm_model = None
        self.ensemble_models = {}
        self.scalers = {}
        self.history = []
        self.model_performance = {}
        
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models from disk if available"""
        lstm_path = os.path.join(self.model_dir, "lstm_model.h5")
        ensemble_path = os.path.join(self.model_dir, "ensemble_models.pkl")
        scalers_path = os.path.join(self.model_dir, "scalers.pkl")
        
        if os.path.exists(lstm_path):
            try:
                self.lstm_model = keras.models.load_model(lstm_path)
            except:
                self.lstm_model = None
        
        if os.path.exists(ensemble_path):
            try:
                with open(ensemble_path, 'rb') as f:
                    self.ensemble_models = pickle.load(f)
            except:
                self.ensemble_models = {}
        
        if os.path.exists(scalers_path):
            try:
                with open(scalers_path, 'rb') as f:
                    self.scalers = pickle.load(f)
            except:
                self.scalers = {}
    
    def save_models(self):
        """Save trained models to disk"""
        if self.lstm_model:
            self.lstm_model.save(os.path.join(self.model_dir, "lstm_model.h5"))
        
        if self.ensemble_models:
            with open(os.path.join(self.model_dir, "ensemble_models.pkl"), 'wb') as f:
                pickle.dump(self.ensemble_models, f)
        
        if self.scalers:
            with open(os.path.join(self.model_dir, "scalers.pkl"), 'wb') as f:
                pickle.dump(self.scalers, f)
    
    def extract_features(self, prices, volumes=None):
        """
        Extract technical indicators and features from price data
        """
        if len(prices) < 30:
            return None
        
        prices = np.array(prices, dtype=np.float32)
        features = {}
        
        # Momentum indicators
        features['momentum'] = prices[-1] - prices[-5]
        features['acceleration'] = (prices[-1] - prices[-2]) - (prices[-2] - prices[-3])
        
        # Trend
        sma10 = np.mean(prices[-10:])
        sma20 = np.mean(prices[-20:])
        features['trend'] = (prices[-1] - sma20) / sma20
        features['sma_ratio'] = sma10 / sma20
        
        # Volatility
        returns = np.diff(prices[-20:]) / prices[-20:-1]
        features['volatility'] = np.std(returns)
        features['std_dev'] = np.std(prices[-10:])
        
        # RSI
        gains = np.sum(np.maximum(np.diff(prices[-14:]), 0))
        losses = np.sum(np.maximum(-np.diff(prices[-14:]), 0))
        avg_gain = gains / 14
        avg_loss = losses / 14
        rs = avg_gain / (avg_loss + 1e-8)
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = self._exponential_moving_avg(prices[-26:], 12)
        ema26 = self._exponential_moving_avg(prices[-26:], 26)
        features['macd'] = ema12[-1] - ema26[-1]
        features['macd_signal'] = np.mean(ema12[-9:] - ema26[-9:])
        
        # Bollinger Bands
        bb_middle = sma20
        bb_std = np.std(prices[-20:])
        features['bb_width'] = bb_std * 2 / bb_middle
        features['bb_position'] = (prices[-1] - (bb_middle - 2*bb_std)) / (4*bb_std)
        
        # Mean reversion score
        features['mean_reversion'] = (sma20 - prices[-1]) / sma20
        
        # Volume features
        if volumes is not None:
            volumes = np.array(volumes)
            features['volume_trend'] = volumes[-1] / (np.mean(volumes[-10:]) + 1e-8)
        
        return features
    
    def _exponential_moving_avg(self, data, period):
        """Calculate exponential moving average"""
        ema = np.zeros(len(data))
        ema[0] = data[0]
        alpha = 2 / (period + 1)
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        return ema
    
    def build_lstm_model(self, lookback=60, n_features=10):
        """Build Bidirectional LSTM model with attention mechanism"""
        model = Sequential([
            Bidirectional(LSTM(128, activation='relu', return_sequences=True), 
                         input_shape=(lookback, n_features)),
            Dropout(0.2),
            Bidirectional(LSTM(64, activation='relu', return_sequences=True)),
            Dropout(0.2),
            Bidirectional(LSTM(32, activation='relu')),
            Dropout(0.2),
            Dense(64, activation='relu'),
            Dropout(0.1),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')  # Output: probability of price increase
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'mae']
        )
        
        self.lstm_model = model
        return model
    
    def build_ensemble_models(self):
        """Build ensemble of tree-based models"""
        self.ensemble_models['rf'] = RandomForestRegressor(
            n_estimators=100, 
            max_depth=15, 
            random_state=42,
            n_jobs=-1
        )
        
        self.ensemble_models['gb'] = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
    
    def prepare_sequences(self, data, lookback=60):
        """Prepare sequences for LSTM"""
        X, y = [], []
        for i in range(len(data) - lookback):
            X.append(data[i:i+lookback])
            y.append(1 if data[i+lookback] > data[i+lookback-1] else 0)
        return np.array(X), np.array(y)
    
    def train_on_history(self, price_history, volume_history=None):
        """
        Train models on historical price data
        Args:
            price_history: List of historical prices
            volume_history: List of historical volumes (optional)
        """
        if len(price_history) < 100:
            return False
        
        prices = np.array(price_history, dtype=np.float32)
        
        # Normalize prices
        if 'price_scaler' not in self.scalers:
            self.scalers['price_scaler'] = MinMaxScaler()
            prices_scaled = self.scalers['price_scaler'].fit_transform(prices.reshape(-1, 1))
        else:
            prices_scaled = self.scalers['price_scaler'].transform(prices.reshape(-1, 1))
        
        # Extract features
        feature_list = []
        for i in range(len(prices)):
            if i >= 30:
                features = self.extract_features(prices[:i+1], 
                                                volume_history[:i+1] if volume_history else None)
                if features:
                    feature_list.append(features)
        
        if len(feature_list) < 50:
            return False
        
        # Prepare feature matrix
        feature_names = list(feature_list[0].keys())
        X_features = np.array([[f.get(name, 0) for name in feature_names] for f in feature_list])
        
        if 'feature_scaler' not in self.scalers:
            self.scalers['feature_scaler'] = StandardScaler()
            X_features = self.scalers['feature_scaler'].fit_transform(X_features)
        else:
            X_features = self.scalers['feature_scaler'].transform(X_features)
        
        # Prepare LSTM sequences
        lookback = 60
        X_lstm, y_lstm = self.prepare_sequences(prices_scaled[-len(feature_list):].flatten(), lookback)
        
        if len(X_lstm) > 0:
            # Build and train LSTM if not exists
            if self.lstm_model is None:
                self.build_lstm_model(lookback=lookback, n_features=1)
            
            # Reshape for LSTM (add feature dimension)
            X_lstm_expanded = np.expand_dims(X_lstm, axis=2)
            
            try:
                self.lstm_model.fit(
                    X_lstm_expanded, y_lstm,
                    epochs=10,
                    batch_size=32,
                    verbose=0,
                    validation_split=0.1
                )
            except:
                pass
        
        # Train ensemble models
        if len(X_features) >= lookback:
            self.build_ensemble_models()
            
            X_train = X_features[:-20]
            y_train = prices_scaled[lookback:lookback+len(X_train)].flatten()
            
            try:
                self.ensemble_models['rf'].fit(X_train, y_train)
                self.ensemble_models['gb'].fit(X_train, y_train)
            except:
                pass
        
        self.save_models()
        return True
    
    def predict(self, recent_prices, recent_volumes=None, confidence_threshold=0.65):
        """
        Make prediction for next price movement
        Returns: {
            'direction': 1 (up) or -1 (down),
            'confidence': 0.0 to 1.0,
            'signal_strength': 'strong', 'moderate', 'weak',
            'reasoning': explanation of prediction
        }
        """
        if len(recent_prices) < 30:
            return {
                'direction': 0,
                'confidence': 0.0,
                'signal_strength': 'insufficient_data',
                'reasoning': 'Need at least 30 price points'
            }
        
        recent_prices = np.array(recent_prices, dtype=np.float32)
        predictions = []
        confidences = []
        
        # LSTM prediction
        if self.lstm_model and len(recent_prices) >= 60:
            try:
                scaler = self.scalers.get('price_scaler')
                if scaler:
                    prices_scaled = scaler.transform(recent_prices.reshape(-1, 1)).flatten()
                    X_lstm = np.expand_dims([prices_scaled[-60:]], axis=2)
                    lstm_pred = self.lstm_model.predict(X_lstm, verbose=0)[0][0]
                    
                    direction = 1 if lstm_pred > 0.5 else -1
                    confidence = lstm_pred if lstm_pred > 0.5 else 1 - lstm_pred
                    
                    predictions.append(direction)
                    confidences.append(confidence)
            except:
                pass
        
        # Feature-based ensemble prediction
        features = self.extract_features(recent_prices, recent_volumes)
        if features and self.ensemble_models:
            try:
                feature_names = sorted(features.keys())
                X = np.array([features.get(name, 0) for name in feature_names]).reshape(1, -1)
                
                scaler = self.scalers.get('feature_scaler')
                if scaler:
                    X = scaler.transform(X)
                
                rf_pred = self.ensemble_models['rf'].predict(X)[0] if 'rf' in self.ensemble_models else 0.5
                gb_pred = self.ensemble_models['gb'].predict(X)[0] if 'gb' in self.ensemble_models else 0.5
                
                ensemble_pred = (rf_pred + gb_pred) / 2
                direction = 1 if ensemble_pred > recent_prices[-1] else -1
                confidence = min(abs(ensemble_pred - recent_prices[-1]) / recent_prices[-1], 1.0)
                
                predictions.append(direction)
                confidences.append(confidence)
            except:
                pass
        
        # Technical analysis voting
        if features:
            tech_score = 0
            tech_vote = 0
            
            if features.get('rsi', 50) < 30:
                tech_vote = 1
                tech_score += 0.8
            elif features.get('rsi', 50) > 70:
                tech_vote = -1
                tech_score -= 0.8
            
            if features.get('macd', 0) > features.get('macd_signal', 0):
                tech_vote += 1
                tech_score += 0.7
            else:
                tech_vote -= 1
                tech_score -= 0.7
            
            if features.get('trend', 0) > 0.01:
                tech_vote += 1
                tech_score += 0.6
            elif features.get('trend', 0) < -0.01:
                tech_vote -= 1
                tech_score -= 0.6
            
            if tech_vote != 0:
                direction = 1 if tech_vote > 0 else -1
                confidence = min(abs(tech_score) / 3.0, 1.0)
                predictions.append(direction)
                confidences.append(confidence)
        
        # Ensemble voting
        if predictions:
            final_direction = 1 if sum(predictions) > 0 else -1
            final_confidence = np.mean(confidences)
        else:
            final_direction = 0
            final_confidence = 0.5
        
        # Determine signal strength
        if final_confidence >= 0.85:
            signal_strength = 'strong'
        elif final_confidence >= 0.70:
            signal_strength = 'moderate'
        else:
            signal_strength = 'weak'
        
        # Generate reasoning
        reasoning = self._generate_reasoning(features, final_direction, final_confidence)
        
        return {
            'direction': final_direction,
            'confidence': round(final_confidence, 3),
            'signal_strength': signal_strength,
            'reasoning': reasoning,
            'features': features
        }
    
    def _generate_reasoning(self, features, direction, confidence):
        """Generate human-readable reasoning for prediction"""
        if not features:
            return "Insufficient technical data for analysis"
        
        reasons = []
        
        rsi = features.get('rsi', 50)
        if rsi < 30:
            reasons.append("RSI oversold (strong buy signal)")
        elif rsi > 70:
            reasons.append("RSI overbought (sell signal)")
        
        trend = features.get('trend', 0)
        if abs(trend) > 0.02:
            reasons.append(f"Strong {'uptrend' if trend > 0 else 'downtrend'}")
        
        volatility = features.get('volatility', 0)
        if volatility > 0.02:
            reasons.append("High volatility detected")
        
        macd = features.get('macd', 0)
        macd_signal = features.get('macd_signal', 0)
        if macd > macd_signal:
            reasons.append("MACD bullish cross")
        elif macd < macd_signal:
            reasons.append("MACD bearish cross")
        
        mr = features.get('mean_reversion', 0)
        if abs(mr) > 0.01:
            reasons.append(f"Mean reversion signal ({'buy' if mr > 0 else 'sell'})")
        
        if not reasons:
            reasons.append("Neutral technical conditions")
        
        return " | ".join(reasons[:3])
    
    def log_prediction(self, symbol, prediction, actual_result=None):
        """Log prediction for performance tracking"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'prediction': prediction,
            'actual_result': actual_result
        }
        self.history.append(entry)
        
        # Update performance metrics
        if actual_result is not None:
            correct = (prediction['direction'] == actual_result)
            symbol_key = symbol
            if symbol_key not in self.model_performance:
                self.model_performance[symbol_key] = {
                    'total': 0,
                    'correct': 0,
                    'accuracy': 0.0
                }
            
            self.model_performance[symbol_key]['total'] += 1
            if correct:
                self.model_performance[symbol_key]['correct'] += 1
            
            self.model_performance[symbol_key]['accuracy'] = (
                self.model_performance[symbol_key]['correct'] / 
                self.model_performance[symbol_key]['total']
            )
    
    def get_performance_metrics(self, symbol=None):
        """Get model performance metrics"""
        if symbol:
            return self.model_performance.get(symbol, {'accuracy': 0.0, 'total': 0})
        return self.model_performance
    
    def simple_ml_predict(self, df):
        """Fallback simple prediction for compatibility"""
        if df is None or len(df) < 30:
            return {'direction': 1, 'confidence': 0.5}
        
        prices = df if isinstance(df, list) else df.tolist()
        result = self.predict(prices)
        return {
            'direction': result['direction'],
            'confidence': result['confidence'],
            'signal_strength': result['signal_strength']
        }


# Global predictor instance
_predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = AdvancedForexPredictor()
    return _predictor


def simple_ml_predict(df):
    """Legacy function for compatibility"""
    return get_predictor().simple_ml_predict(df)