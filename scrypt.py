#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Offline UVB-76 Blockchain with Real Genesis Block
A post-apocalyptic blockchain game anchored by UVB-76 radio signals

Genesis block: "HЖTИ 76472 ПEPEДEPЖKA 4301 8808" (real UVB-76 transmission)
All participants start from this block.

Key feature: Genesis blocks are considered identical if they have the same
station message, even if timestamps differ.
"""

import hashlib
import json
import time
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# CONSTANTS
# ============================================================================

# Реальное сообщение УВБ-76, которое становится генезис-блоком
GENESIS_MESSAGE = "HЖTИ 76472 ПEPEДEPЖKA 4301 8808"


class Transaction:
    """User message (transaction)."""
    
    def __init__(self, sender: str, recipient: str, message: str, timestamp: Optional[float] = None):
        self.sender = sender
        self.recipient = recipient
        self.message = message
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Computes the transaction hash."""
        data = f"{self.sender}{self.recipient}{self.message}{self.timestamp}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'message': self.message,
            'timestamp': self.timestamp,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        tx = cls(
            sender=data['sender'],
            recipient=data['recipient'],
            message=data['message'],
            timestamp=data['timestamp']
        )
        if tx.hash != data['hash']:
            raise ValueError(f"Transaction hash mismatch! Expected {tx.hash[:16]}..., got {data['hash'][:16]}...")
        return tx
    
    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return f"Tx[{self.hash[:8]}...] {self.sender}→{self.recipient}: '{self.message[:30]}' @ {dt}"


class Block:
    """Main blockchain block with transaction hashes."""
    
    def __init__(self, index: int, previous_hash: str, station_message: str,
                 tx_hashes: Optional[List[str]] = None, timestamp: Optional[float] = None):
        self.index = index
        self.previous_hash = previous_hash
        self.station_message = station_message
        self.tx_hashes = sorted(tx_hashes) if tx_hashes is not None else []
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.station_message_hash = hashlib.sha256(station_message.encode('utf-8')).hexdigest()
        self.block_hash = self.compute_block_hash()

    def compute_block_hash(self) -> str:
        """
        Computes the block hash including all fields.
        For genesis block (index=0), timestamp is EXCLUDED from hash calculation
        to allow different nodes to have the same genesis block even if created
        at different times.
        """
        block_data = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'station_message_hash': self.station_message_hash,
            'tx_hashes': self.tx_hashes
        }
        
        # For non-genesis blocks, include timestamp in hash
        if self.index > 0:
            block_data['timestamp'] = self.timestamp
            
        block_string = json.dumps(block_data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'station_message': self.station_message,
            'timestamp': self.timestamp,
            'station_message_hash': self.station_message_hash,
            'tx_hashes': self.tx_hashes,
            'block_hash': self.block_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        required_fields = ['index', 'previous_hash', 'station_message', 
                          'timestamp', 'station_message_hash', 'tx_hashes', 'block_hash']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in block: {field}")
        
        block = cls(
            index=data['index'],
            previous_hash=data['previous_hash'],
            station_message=data['station_message'],
            tx_hashes=data['tx_hashes'],
            timestamp=data['timestamp']
        )
        
        if block.block_hash != data['block_hash']:
            raise ValueError(f"Block hash mismatch for block #{data['index']}!")
        
        return block
    
    def __str__(self) -> str:
        dt = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return f"Block #{self.index} [{self.block_hash[:8]}...] @ {dt} - {len(self.tx_hashes)} tx"


class BlockchainNode:
    """Main blockchain node with chain and transaction pool."""
    
    def __init__(self, storage_file: str = 'blockchain.json', tx_pool_file: str = 'tx_pool.json'):
        self.storage_file = storage_file
        self.tx_pool_file = tx_pool_file
        self.chain: List[Block] = []
        self.tx_pool: Dict[str, Transaction] = {}
        self.load_chain()
        self.load_tx_pool()

    # ------------------------------------------------------------------------
    # Genesis Block (REAL UVB-76 MESSAGE)
    # ------------------------------------------------------------------------

    def create_genesis_block(self) -> Block:
        """
        Creates the genesis block using the REAL UVB-76 message.
        This ensures all participants start from the same block.
        """
        print(f"\n🔰 Creating GENESIS block from REAL UVB-76 message:")
        print(f"   \"{GENESIS_MESSAGE}\"")
        
        return Block(
            index=0,
            previous_hash='0',
            station_message=GENESIS_MESSAGE,
            tx_hashes=[]
        )

    # ------------------------------------------------------------------------
    # Chain Management
    # ------------------------------------------------------------------------

    def load_chain(self):
        """Loads the blockchain from file. If not exists, creates genesis block."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    print(f"⚠️  Warning: {self.storage_file} does not contain a list. Creating new chain with REAL genesis.")
                    self.chain = [self.create_genesis_block()]
                    self.save_chain()
                    return
                
                self.chain = []
                for block_data in data:
                    try:
                        block = Block.from_dict(block_data)
                        self.chain.append(block)
                    except ValueError as e:
                        print(f"⚠️  Warning: Skipping invalid block: {e}")
                
                print(f"✅ Chain loaded from {self.storage_file}. Blocks: {len(self.chain)}")
                
                # Verify genesis block is correct
                if len(self.chain) > 0:
                    if self.chain[0].station_message != GENESIS_MESSAGE:
                        print("\n⚠️  WARNING: Your genesis block is different from the agreed standard!")
                        print(f"   Your genesis: \"{self.chain[0].station_message}\"")
                        print(f"   Standard:     \"{GENESIS_MESSAGE}\"")
                        print("   This may cause synchronization problems with other nodes.\n")
                
            except json.JSONDecodeError:
                print(f"❌ Error: {self.storage_file} is not valid JSON. Creating new chain with REAL genesis.")
                self.chain = [self.create_genesis_block()]
                self.save_chain()
            except Exception as e:
                print(f"❌ Error loading chain: {e}. Creating new chain with REAL genesis.")
                self.chain = [self.create_genesis_block()]
                self.save_chain()
        else:
            print("\n📻 FIRST RUN DETECTED")
            print(f"Creating genesis block from REAL UVB-76 message:")
            print(f"   \"{GENESIS_MESSAGE}\"")
            print("\nThis ensures all participants start from the same block.")
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def save_chain(self):
        """Saves the blockchain to file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([block.to_dict() for block in self.chain], f, 
                         ensure_ascii=False, indent=2)
            print(f"✅ Chain saved to {self.storage_file}")
        except Exception as e:
            print(f"❌ Error saving chain: {e}")

    # ------------------------------------------------------------------------
    # Transaction Pool Management
    # ------------------------------------------------------------------------

    def load_tx_pool(self):
        """Loads the transaction pool from file."""
        if os.path.exists(self.tx_pool_file):
            try:
                with open(self.tx_pool_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, dict):
                    print(f"⚠️  Warning: {self.tx_pool_file} does not contain a dictionary. Starting with empty pool.")
                    self.tx_pool = {}
                    return
                
                self.tx_pool = {}
                for tx_hash, tx_data in data.items():
                    try:
                        tx = Transaction.from_dict(tx_data)
                        if tx.hash != tx_hash:
                            print(f"⚠️  Warning: Hash mismatch for transaction: key={tx_hash[:16]}..., actual={tx.hash[:16]}...")
                        self.tx_pool[tx.hash] = tx
                    except ValueError as e:
                        print(f"⚠️  Warning: Skipping invalid transaction {tx_hash[:16]}...: {e}")
                
                print(f"✅ Transaction pool loaded. Transactions: {len(self.tx_pool)}")
                    
            except json.JSONDecodeError:
                print(f"❌ Error: {self.tx_pool_file} is not valid JSON. Starting with empty pool.")
                self.tx_pool = {}
            except Exception as e:
                print(f"❌ Error loading transaction pool: {e}. Starting with empty pool.")
                self.tx_pool = {}
        else:
            self.tx_pool = {}

    def save_tx_pool(self):
        """Saves the transaction pool to file."""
        try:
            with open(self.tx_pool_file, 'w', encoding='utf-8') as f:
                data = {tx_hash: tx.to_dict() for tx_hash, tx in self.tx_pool.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Transaction pool saved to {self.tx_pool_file}")
        except Exception as e:
            print(f"❌ Error saving transaction pool: {e}")

    # ------------------------------------------------------------------------
    # Transaction Operations
    # ------------------------------------------------------------------------

    def add_transaction(self, sender: str, recipient: str, message: str) -> str:
        """Creates a new transaction and adds it to the pool."""
        tx = Transaction(sender, recipient, message)
        
        if tx.hash in self.tx_pool:
            print(f"ℹ️  Transaction with hash {tx.hash[:16]}... already exists in pool.")
            return tx.hash
        
        self.tx_pool[tx.hash] = tx
        self.save_tx_pool()
        print(f"\n✅ Transaction created successfully!")
        print(f"   From: {sender}")
        print(f"   To: {recipient}")
        print(f"   Message: {message}")
        print(f"   Hash: {tx.hash}")
        print(f"   Hash (short): {tx.hash[:16]}...")
        return tx.hash

    def find_transaction_by_hash(self, search_hash: str) -> Dict[str, Any]:
        """Finds a transaction by its hash."""
        search_hash = search_hash.strip().lower()
        
        # Search in pool
        for tx_hash, tx in self.tx_pool.items():
            if search_hash in tx_hash:
                return {
                    'found': True,
                    'exact_match': tx_hash == search_hash,
                    'location': 'transaction pool (unconfirmed)',
                    'transaction': tx.to_dict(),
                    'matched_hash': tx_hash
                }
        
        # Search in blocks
        found_in_blocks = []
        for block in self.chain:
            for tx_hash in block.tx_hashes:
                if search_hash in tx_hash:
                    found_in_blocks.append({
                        'block_index': block.index,
                        'block_hash': block.block_hash,
                        'station_message': block.station_message,
                        'timestamp': block.timestamp,
                        'tx_hash': tx_hash
                    })
        
        if found_in_blocks:
            return {
                'found': True,
                'location': f'found in {len(found_in_blocks)} block(s) (confirmed)',
                'blocks': found_in_blocks,
                'note': 'Only hash stored in blockchain, full transaction data not available'
            }
        
        return {'found': False}

    def decrypt_message_by_hash(self, hash_str: str):
        """Shows message details for a given hash."""
        result = self.find_transaction_by_hash(hash_str)
        
        print("\n" + "="*70)
        print(f"🔍 SEARCH RESULTS FOR HASH: {hash_str[:16]}...")
        print("="*70)
        
        if not result['found']:
            print("❌ Transaction not found in pool or any block.")
            return
        
        if 'transaction' in result:
            tx = result['transaction']
            print(f"✅ Found in: {result['location']}")
            if not result.get('exact_match', True):
                print(f"   (Partial match for hash: {result['matched_hash'][:16]}...)")
            
            print("\n📨 MESSAGE DETAILS:")
            print(f"   ┌─────────────────────────────────")
            print(f"   │ From:      {tx['sender']}")
            print(f"   │ To:        {tx['recipient']}")
            print(f"   │ Message:   {tx['message']}")
            dt = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   │ Timestamp: {dt}")
            print(f"   │ Full hash: {tx['hash']}")
            print(f"   └─────────────────────────────────")
            
        else:
            print(f"✅ Hash found in: {result['location']}")
            print("\n⚠️  NOTE: Only the hash is stored in the blockchain.")
            print("   To see the full message, you need the original transaction file.")
            
            print("\n📦 Block information:")
            for i, block_info in enumerate(result['blocks'], 1):
                print(f"\n   ┌─ Block #{block_info['block_index']}")
                print(f"   │ Block hash: {block_info['block_hash'][:16]}...")
                print(f"   │ Station msg: {block_info['station_message'][:40]}...")
                dt = datetime.fromtimestamp(block_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   │ Time: {dt}")
                print(f"   │ Tx hash: {block_info['tx_hash'][:16]}...")
                print(f"   └─────────────────────────────────")

    # ------------------------------------------------------------------------
    # Block Operations
    # ------------------------------------------------------------------------

    def add_block(self, station_message: str, selected_tx_hashes: Optional[List[str]] = None):
        """Adds a new block based on station message and selected transaction hashes."""
        if not station_message.strip():
            print("❌ Station message cannot be empty.")
            return

        # Validate and prepare transaction hashes
        if selected_tx_hashes is None:
            selected_tx_hashes = list(self.tx_pool.keys())
            print(f"ℹ️  Including all {len(selected_tx_hashes)} unconfirmed transactions.")
        else:
            valid_hashes = []
            for h in selected_tx_hashes:
                h = h.strip()
                if h in self.tx_pool:
                    valid_hashes.append(h)
                else:
                    print(f"⚠️  Warning: Hash {h[:16]}... not in pool. Skipping.")
            selected_tx_hashes = valid_hashes
            print(f"ℹ️  Including {len(selected_tx_hashes)} valid transactions.")

        # Create new block
        last_block = self.chain[-1]
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.block_hash,
            station_message=station_message.strip(),
            tx_hashes=selected_tx_hashes
        )
        
        # Add to chain
        self.chain.append(new_block)
        self.save_chain()

        # Remove confirmed transactions from pool
        for h in selected_tx_hashes:
            self.tx_pool.pop(h, None)
        if selected_tx_hashes:
            self.save_tx_pool()
            print(f"✅ Removed {len(selected_tx_hashes)} confirmed transactions from pool.")

        # Display block info
        print(f"\n✅ Block #{new_block.index} added successfully!")
        print(f"   ┌─────────────────────────────────")
        print(f"   │ Station message: {new_block.station_message}")
        print(f"   │ Station msg hash: {new_block.station_message_hash[:16]}...")
        print(f"   │ Transactions: {len(new_block.tx_hashes)}")
        print(f"   │ Block hash: {new_block.block_hash[:16]}...")
        print(f"   │ Previous hash: {new_block.previous_hash[:16]}...")
        dt = datetime.fromtimestamp(new_block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   │ Time: {dt}")
        print(f"   └─────────────────────────────────")

    # ------------------------------------------------------------------------
    # Display Functions
    # ------------------------------------------------------------------------

    def print_chain(self, limit: Optional[int] = None):
        """Prints the blockchain."""
        print("\n" + "="*80)
        print(f"📦 BLOCKCHAIN (total blocks: {len(self.chain)})")
        print("="*80)
        
        if len(self.chain) == 0:
            print("Chain is empty!")
            return
        
        start = 0 if limit is None else max(0, len(self.chain) - limit)
        
        for i in range(start, len(self.chain)):
            block = self.chain[i]
            print(f"\n┌─ Block #{block.index} ".ljust(40, '─'))
            print(f"│ Block hash:    {block.block_hash}")
            
            # Show genesis block specially
            if block.index == 0:
                print(f"│ 🔰 GENESIS BLOCK (REAL UVB-76 MESSAGE)")
            
            print(f"│ Prev hash:     {block.previous_hash[:16]}...")
            print(f"│ Station msg:   {block.station_message}")
            dt = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"│ Time:          {dt}")
            print(f"│ Station hash:  {block.station_message_hash[:16]}...")
            print(f"│ Tx count:      {len(block.tx_hashes)}")
            
            if block.tx_hashes and block.index > 0:  # Don't show genesis block transactions
                print(f"│ Transaction hashes:")
                for j, th in enumerate(block.tx_hashes[:3], 1):
                    print(f"│   {j}. {th[:16]}...")
                if len(block.tx_hashes) > 3:
                    print(f"│   ... and {len(block.tx_hashes)-3} more")
            print(f"└" + "─"*40)

    def print_tx_pool(self):
        """Prints the unconfirmed transaction pool."""
        print("\n" + "="*80)
        print(f"📨 UNCONFIRMED TRANSACTION POOL ({len(self.tx_pool)} transactions)")
        print("="*80)
        
        if not self.tx_pool:
            print("Pool is empty.")
            return
        
        for i, (tx_hash, tx) in enumerate(list(self.tx_pool.items())[:10], 1):
            dt = datetime.fromtimestamp(tx.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{i}. Hash: {tx_hash}")
            print(f"   From: {tx.sender} → To: {tx.recipient}")
            print(f"   Msg: {tx.message[:50]}{'...' if len(tx.message) > 50 else ''}")
            print(f"   Time: {dt}")
        
        if len(self.tx_pool) > 10:
            print(f"\n... and {len(self.tx_pool)-10} more transactions.")

    # ------------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------------

    def verify_chain(self, silent: bool = False) -> bool:
        """Verifies the integrity of the blockchain."""
        if not silent:
            print("\n🔍 Verifying blockchain integrity...")
        
        if len(self.chain) <= 1:
            if not silent:
                print("✅ Chain is intact (only genesis block).")
            return True
        
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            
            if curr.previous_hash != prev.block_hash:
                if not silent:
                    print(f"❌ ERROR: Block #{i} previous_hash doesn't match block #{i-1} hash!")
                return False
            
            if curr.block_hash != curr.compute_block_hash():
                if not silent:
                    print(f"❌ ERROR: Block #{i} hash mismatch!")
                return False
            
            if curr.station_message_hash != hashlib.sha256(curr.station_message.encode('utf-8')).hexdigest():
                if not silent:
                    print(f"❌ ERROR: Block #{i} station message hash mismatch!")
                return False
        
        if not silent:
            print("✅ Chain is intact. All blocks are valid.")
        return True

    # ------------------------------------------------------------------------
    # Synchronization (with genesis block special handling)
    # ------------------------------------------------------------------------

    def sync_with_peer(self, peer_chain_file: str, peer_tx_file: str):
        """
        Synchronizes chain and transaction pool with another node's files.
        Includes special handling for genesis block: blocks are considered
        matching if they have the same station message, even if timestamps differ.
        """
        print("\n" + "="*80)
        print("🔄 SYNCHRONIZING WITH PEER")
        print("="*80)
        
        # --------------------------------------------------------------------
        # Load peer's chain
        # --------------------------------------------------------------------
        if not os.path.exists(peer_chain_file):
            print(f"❌ Error: Peer chain file '{peer_chain_file}' not found.")
            return
        
        try:
            with open(peer_chain_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                print(f"❌ Error: Peer chain file '{peer_chain_file}' is empty.")
                return
                
            peer_chain_data = json.loads(content)
            
            if not isinstance(peer_chain_data, list):
                print(f"❌ Error: Peer chain file must contain a list of blocks.")
                return
            
            peer_chain = []
            for i, block_data in enumerate(peer_chain_data):
                try:
                    block = Block.from_dict(block_data)
                    peer_chain.append(block)
                except ValueError as e:
                    print(f"⚠️  Warning: Skipping invalid block #{i} in peer chain: {e}")
            
            if not peer_chain:
                print("❌ Error: No valid blocks found in peer chain file.")
                return
                
            print(f"✅ Loaded peer chain: {len(peer_chain)} blocks")
            
        except Exception as e:
            print(f"❌ Error reading peer chain file: {e}")
            return

        # --------------------------------------------------------------------
        # Load peer's transaction pool
        # --------------------------------------------------------------------
        peer_tx_pool = {}
        if os.path.exists(peer_tx_file):
            try:
                with open(peer_tx_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    peer_tx_data = json.loads(content)
                    
                    if isinstance(peer_tx_data, dict):
                        for tx_hash, tx_data in peer_tx_data.items():
                            try:
                                tx = Transaction.from_dict(tx_data)
                                peer_tx_pool[tx.hash] = tx
                            except ValueError as e:
                                print(f"⚠️  Warning: Skipping invalid transaction {tx_hash[:16]}...: {e}")
                        
                        print(f"✅ Loaded peer tx pool: {len(peer_tx_pool)} transactions")
            except Exception as e:
                print(f"⚠️  Warning: Error reading peer tx file: {e}")

        # --------------------------------------------------------------------
        # SPECIAL HANDLING FOR GENESIS BLOCK
        # --------------------------------------------------------------------
        print("\n🔍 Checking genesis blocks...")
        
        genesis_self = self.chain[0]
        genesis_peer = peer_chain[0]
        
        # Check if station messages match
        if genesis_self.station_message == genesis_peer.station_message:
            # Check if station message hashes match
            if genesis_self.station_message_hash == genesis_peer.station_message_hash:
                print("✅ Genesis blocks MATCH (same station message)!")
                print(f"   Your message: \"{genesis_self.station_message}\"")
                print(f"   Peer message: \"{genesis_peer.station_message}\"")
                print("   (Timestamps are ignored for genesis comparison)")
                
                # Set common prefix to at least 1, even if block hashes differ
                common_len = 1
            else:
                print("\n❌ CRITICAL: Genesis station message hashes are different!")
                print(f"   Your hash:     {genesis_self.station_message_hash[:16]}...")
                print(f"   Peer's hash:   {genesis_peer.station_message_hash[:16]}...")
                print("   This means the genesis messages are actually different!")
                print("   Synchronization impossible - different blockchains!")
                return
        else:
            print("\n❌ CRITICAL: Genesis messages are different!")
            print(f"   Your genesis:  \"{genesis_self.station_message}\"")
            print(f"   Peer's genesis: \"{genesis_peer.station_message}\"")
            print("   Synchronization impossible - different blockchains!")
            return

        # --------------------------------------------------------------------
        # Compare remaining chains (starting from block 1)
        # --------------------------------------------------------------------
        print("\n📊 Comparing chains from block #1...")
        
        # Find common prefix starting from block 1
        max_common = min(len(self.chain), len(peer_chain))
        for i in range(1, max_common):
            if self.chain[i].block_hash == peer_chain[i].block_hash:
                common_len = i + 1
            else:
                break

        print(f"   Our chain: {len(self.chain)} blocks")
        print(f"   Peer chain: {len(peer_chain)} blocks")
        print(f"   Common prefix: {common_len} blocks (including genesis)")

        # --------------------------------------------------------------------
        # Chain resolution
        # --------------------------------------------------------------------
        if len(peer_chain) > len(self.chain) and common_len == len(self.chain):
            print("\n✅ Our chain is a prefix of peer's longer chain. Accepting peer chain.")
            self.chain = peer_chain
            self.save_chain()
            
        elif len(peer_chain) < len(self.chain) and common_len == len(peer_chain):
            print("\nℹ️  Our chain is longer and contains peer's chain. No update needed.")
            
        elif common_len < len(self.chain) and common_len < len(peer_chain):
            print("\n⚠️  WARNING: Chains have diverged after block #{}!".format(common_len-1))
            print(f"   First divergence at block #{common_len}")
            print(f"   Our block:  {self.chain[common_len].block_hash[:16]}...")
            print(f"   Peer block: {peer_chain[common_len].block_hash[:16]}...")
            
            if len(self.chain) > len(peer_chain):
                print(f"   Our chain is longer ({len(self.chain)} vs {len(peer_chain)}), keeping ours.")
            elif len(peer_chain) > len(self.chain):
                print(f"   Peer chain is longer ({len(peer_chain)} vs {len(self.chain)}), but they diverged.")
                print("   Manual resolution required.")
            else:
                print("   Both chains have same length but different content.")
                print("   Manual resolution required.")
            
        else:
            print("\n✅ Chains are identical.")

        # --------------------------------------------------------------------
        # Merge transaction pools
        # --------------------------------------------------------------------
        if peer_tx_pool:
            before_merge = len(self.tx_pool)
            
            for tx_hash, tx in peer_tx_pool.items():
                if tx_hash not in self.tx_pool:
                    self.tx_pool[tx_hash] = tx
            
            if len(self.tx_pool) > before_merge:
                self.save_tx_pool()
                print(f"\n✅ Transaction pool merged: +{len(self.tx_pool)-before_merge} new transactions")
                print(f"   Total transactions now: {len(self.tx_pool)}")
            else:
                print("\n✅ Transaction pools already synchronized.")
        else:
            print("\nℹ️  No peer transactions to merge.")

        print("\n" + "="*80)
        print("✅ SYNCHRONIZATION COMPLETE")
        print("="*80)

    # ------------------------------------------------------------------------
    # Import/Export
    # ------------------------------------------------------------------------

    def export_tx_pool(self, filename: str):
        """Exports the transaction pool to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                data = {tx_hash: tx.to_dict() for tx_hash, tx in self.tx_pool.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Transaction pool exported to {filename} ({len(self.tx_pool)} transactions)")
        except Exception as e:
            print(f"❌ Error exporting transaction pool: {e}")

    def import_tx_pool(self, filename: str):
        """Imports transactions from a file and adds to pool."""
        if not os.path.exists(filename):
            print(f"❌ Error: File '{filename}' not found.")
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print(f"⚠️  Warning: File '{filename}' is empty.")
                return
                
            data = json.loads(content)
            
            if not isinstance(data, dict):
                print(f"❌ Error: File must contain a dictionary of transactions.")
                return
            
            imported = 0
            skipped = 0
            
            for tx_hash, tx_data in data.items():
                try:
                    tx = Transaction.from_dict(tx_data)
                    
                    if tx.hash in self.tx_pool:
                        skipped += 1
                        continue
                    
                    self.tx_pool[tx.hash] = tx
                    imported += 1
                    
                except ValueError as e:
                    print(f"⚠️  Warning: Skipping invalid transaction {tx_hash[:16]}...: {e}")
                    skipped += 1
            
            if imported > 0:
                self.save_tx_pool()
            
            print(f"\n✅ Import complete:")
            print(f"   Imported: {imported}")
            print(f"   Skipped: {skipped}")
            print(f"   Total in pool now: {len(self.tx_pool)}")
            
        except json.JSONDecodeError:
            print(f"❌ Error: File is not valid JSON.")
        except Exception as e:
            print(f"❌ Error importing transactions: {e}")


# ============================================================================
# MAIN MENU
# ============================================================================

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main program loop."""
    
    print("="*80)
    print("📻 OFFLINE UVB-76 BLOCKCHAIN")
    print("="*80)
    print(f"Genesis block: \"{GENESIS_MESSAGE}\"")
    print("All participants start from this REAL UVB-76 transmission")
    print("Genesis blocks are considered identical based on message, not timestamp")
    print("="*80)
    
    # Create node (will automatically create genesis block if needed)
    node = BlockchainNode()
    
    while True:
        print("\n" + "="*80)
        print(f"Chain: {len(node.chain)} blocks | Pool: {len(node.tx_pool)} transactions")
        print("-"*80)
        print("1. 📝 Add new station message (block)")
        print("2. 💬 Create personal message (transaction)")
        print("3. 📋 Show unconfirmed transaction pool")
        print("4. 🔍 Decrypt/show message by hash")
        print("5. 📚 Show last 10 blocks")
        print("6. 📖 Show entire chain")
        print("7. ✅ Verify chain integrity")
        print("8. 🔄 Synchronize with another node (files)")
        print("9. 📤 Export transaction pool to file")
        print("10. 📥 Import transactions from file")
        print("0. 🚪 Exit")
        print("-"*80)
        
        choice = input("Choose action (0-10): ").strip()

        if choice == '1':
            print("\n📻 Enter the message from UVB-76:")
            print("   Example: 'БРОНЯ 00 19 85 АКУЛА'")
            msg = input("Message: ").strip()
            
            if msg:
                print("\nInclude transactions in this block?")
                include_all = input("Include all unconfirmed transactions? (y/n): ").strip().lower()
                
                if include_all == 'y':
                    node.add_block(msg)
                else:
                    if node.tx_pool:
                        node.print_tx_pool()
                        tx_hashes = input("\nEnter transaction hashes (comma-separated, or empty for none): ").strip()
                        if tx_hashes:
                            selected = [h.strip() for h in tx_hashes.split(',') if h.strip()]
                            node.add_block(msg, selected)
                        else:
                            node.add_block(msg, [])
                    else:
                        print("ℹ️  Transaction pool is empty. Creating block without transactions.")
                        node.add_block(msg, [])
            else:
                print("❌ Message cannot be empty.")

        elif choice == '2':
            print("\n💬 Create a new personal message:")
            sender = input("Your name (sender): ").strip()
            recipient = input("To: ").strip()
            message = input("Message text: ").strip()
            
            if sender and recipient and message:
                node.add_transaction(sender, recipient, message)
            else:
                print("❌ All fields must be filled.")

        elif choice == '3':
            node.print_tx_pool()

        elif choice == '4':
            print("\n🔍 Enter transaction hash to decrypt/show:")
            hash_input = input("Hash: ").strip()
            
            if hash_input:
                node.decrypt_message_by_hash(hash_input)
            else:
                print("❌ Hash cannot be empty.")

        elif choice == '5':
            node.print_chain(limit=10)

        elif choice == '6':
            node.print_chain()

        elif choice == '7':
            node.verify_chain()

        elif choice == '8':
            print("\n🔄 Synchronize with another node:")
            print("   You need both files from the peer.")
            
            chain_file = input("\nPeer's chain filename (e.g., peer_blockchain.json): ").strip()
            tx_file = input("Peer's transaction pool filename (e.g., peer_tx.json): ").strip()
            
            if chain_file and tx_file:
                node.sync_with_peer(chain_file, tx_file)
            else:
                print("❌ Both filenames are required.")

        elif choice == '9':
            print("\n📤 Export transaction pool:")
            export_file = input("Export filename (e.g., my_transactions.json): ").strip()
            
            if export_file:
                node.export_tx_pool(export_file)
            else:
                print("❌ Filename cannot be empty.")

        elif choice == '10':
            print("\n📥 Import transactions from file:")
            import_file = input("Import filename: ").strip()
            
            if import_file:
                node.import_tx_pool(import_file)
            else:
                print("❌ Filename cannot be empty.")

        elif choice == '0':
            print("\n👋 Goodbye! Stay tuned to UVB-76!")
            break

        else:
            print("❌ Invalid choice. Please enter a number between 0 and 10.")

        input("\nPress Enter to continue...")
        clear_screen()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Stay tuned to UVB-76!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue.")
