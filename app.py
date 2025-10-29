from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
logging.basicConfig(level=logging.INFO)

# Configure your wallet connection from environment variables
WALLET_HOST = os.environ['WALLET_HOST']
WALLET_PORT = int(os.environ['WALLET_PORT'])
WALLET_PASSWORD = os.environ['WALLET_PASSWORD']

# Flask app configuration from environment variables
FLASK_HOST = os.environ['FLASK_HOST']
FLASK_PORT = int(os.environ['FLASK_PORT'])
FLASK_DEBUG = os.environ['FLASK_DEBUG'].lower() == 'true'

def get_wallet():
    """Get wallet instance with error handling"""
    try:
        backend = JSONRPCWallet(host=WALLET_HOST, port=WALLET_PORT)
        wallet = Wallet(backend)
        return wallet
    except Exception as e:
        app.logger.error(f"Failed to connect to wallet: {e}")
        return None

def get_wallet_data():
    """Get all wallet data for rendering"""
    wallet = get_wallet()
    if not wallet:
        return None
    
    try:
        # Get the primary address
        primary_address = wallet.address()
        
        # Get all addresses in the first account
        addresses = wallet.addresses()
        
        # Get wallet balance
        balance = wallet.balance()
        
        # Get incoming transactions
        incoming = wallet.incoming(unconfirmed=True)
        incoming_transactions = []
        for payment in incoming:
            confirmations = wallet.confirmations(payment)
            
            if confirmations == 0:
                status = "Unconfirmed"
                status_class = "unconfirmed"
            elif confirmations < 10:
                status = f"Confirming {confirmations}/10"
                status_class = "confirming"
            else:
                status = "Confirmed"
                status_class = "confirmed"
            
            incoming_transactions.append({
                'amount': str(payment.amount),
                'address': str(payment.local_address) if payment.local_address else 'Unknown',
                'txid': payment.transaction.hash,
                'height': payment.transaction.height,
                'confirmations': confirmations,
                'status': status,
                'status_class': status_class
            })
        
        # Get outgoing transactions
        outgoing = wallet.outgoing(unconfirmed=True)
        outgoing_transactions = []
        for payment in outgoing:
            confirmations = wallet.confirmations(payment)
            
            if confirmations == 0:
                status = "Unconfirmed"
                status_class = "unconfirmed"
            elif confirmations < 10:
                status = f"Confirming {confirmations}/10"
                status_class = "confirming"
            else:
                status = "Confirmed"
                status_class = "confirmed"
            
            outgoing_transactions.append({
                'amount': str(payment.amount),
                'address': str(payment.local_address) if payment.local_address else 'Unknown',
                'txid': payment.transaction.hash,
                'height': payment.transaction.height,
                'confirmations': confirmations,
                'status': status,
                'status_class': status_class,
                'fee': str(payment.transaction.fee) if hasattr(payment.transaction, 'fee') else '0'
            })
        
        return {
            'primary_address': str(primary_address),
            'all_addresses': [str(addr) for addr in addresses],
            'balance': str(balance),
            'incoming_transactions': incoming_transactions,
            'outgoing_transactions': outgoing_transactions
        }
    except Exception as e:
        app.logger.error(f"Error getting wallet info: {e}")
        return None

@app.route('/')
def index():
    """Main page showing current wallet address and all data"""
    wallet_data = get_wallet_data()
    if not wallet_data:
        return render_template('error.html', 
                             error="Could not connect to Monero wallet. Please ensure monero-wallet-rpc is running.")
    
    return render_template('index.html', **wallet_data)

@app.route('/new_address', methods=['POST'])
def new_address():
    """Create a new subaddress and redirect to main page"""
    wallet = get_wallet()
    if not wallet:
        flash('Could not connect to wallet', 'error')
        return redirect(url_for('index'))
    
    try:
        # Create new subaddress
        new_addr, index = wallet.new_address()
        flash(f'New address generated successfully! Index: {index}', 'success')
    except Exception as e:
        app.logger.error(f"Error creating new address: {e}")
        flash(f'Error creating new address: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    """Send a transaction to specified address and redirect to main page"""
    wallet = get_wallet()
    if not wallet:
        flash('Could not connect to wallet', 'error')
        return redirect(url_for('index'))
    
    try:
        to_address = request.form.get('address', '').strip()
        amount = request.form.get('amount', 0)
        
        if not to_address:
            flash('Recipient address is required', 'error')
            return redirect(url_for('index'))
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than 0', 'error')
                return redirect(url_for('index'))
        except (ValueError, TypeError):
            flash('Invalid amount format', 'error')
            return redirect(url_for('index'))
        
        # Check if wallet has sufficient balance
        balance = wallet.balance()
        if amount > float(balance):
            flash(f'Insufficient balance. Available: {balance} XMR', 'error')
            return redirect(url_for('index'))
        
        # Send the transaction
        txs = wallet.transfer(to_address, amount)
        
        if txs:
            # Get the first transaction (usually there's only one)
            tx = txs[0]
            flash(f'Transaction sent successfully! TX: {tx.hash} Fee: {tx.fee} XMR', 'success')
        else:
            flash('Failed to send transaction', 'error')
        
    except Exception as e:
        app.logger.error(f"Error sending transaction: {e}")
        flash(f'Error sending transaction: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# Keep JSON API endpoints for potential future use
@app.route('/wallet_info')
def wallet_info():
    """Get current wallet information"""
    wallet_data = get_wallet_data()
    if not wallet_data:
        return jsonify({'success': False, 'error': 'Could not connect to wallet'})
    
    return jsonify({
        'success': True,
        'addresses': wallet_data['all_addresses'],
        'balance': wallet_data['balance'],
        'address_count': len(wallet_data['all_addresses'])
    })

@app.route('/transactions')
def get_transactions():
    """Get incoming transactions with confirmation status"""
    wallet_data = get_wallet_data()
    if not wallet_data:
        return jsonify({'success': False, 'error': 'Could not connect to wallet'})
    
    return jsonify({
        'success': True,
        'transactions': wallet_data['incoming_transactions']
    })

@app.route('/outgoing_transactions')
def get_outgoing_transactions():
    """Get outgoing transactions with confirmation status"""
    wallet_data = get_wallet_data()
    if not wallet_data:
        return jsonify({'success': False, 'error': 'Could not connect to wallet'})
    
    return jsonify({
        'success': True,
        'transactions': wallet_data['outgoing_transactions']
    })

if __name__ == '__main__':
    print("Starting Monero Wallet Web App...")
    print(f"Make sure monero-wallet-rpc is running on {WALLET_HOST}:{WALLET_PORT}")
    print(f"Access the app at http://{FLASK_HOST}:{FLASK_PORT}")
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
