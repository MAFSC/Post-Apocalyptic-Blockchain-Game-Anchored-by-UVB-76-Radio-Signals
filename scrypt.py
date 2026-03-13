import hashlib
import json
import time
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

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
            raise ValueError("Transaction hash does not match!")
        return tx

class Block:
    """Main blockchain block, now includes a list of transaction hashes."""
    def __init__(self, index: int, previous_hash: str, station_message: str,
                 tx_hashes: Optional[List[str]] = None, timestamp: Optional[float] = None):
        self.index = index
        self.previous_hash = previous_hash
        self.station_message = station_message
        self.tx_hashes = tx_hashes if tx_hashes is not None else []
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.station_message_hash = hashlib.sha256(station_message.encode('utf-8')).hexdigest()
        self.block_hash = self.compute_block_hash()

    def compute_block_hash(self) -> str:
        """Block hash includes previous hash, index, timestamp, station message hash, and the list of transaction hashes."""
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'station_message_hash': self.station_message_hash,
            'tx_hashes': sorted(self.tx_hashes)  # sort for determinism
        }, sort_keys=True).encode('utf-8')
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
        block = cls(
            index=data['index'],
            previous_hash=data['previous_hash'],
            station_message=data['station_message'],
            tx_hashes=data['tx_hashes'],
            timestamp=data['timestamp']
        )
        if block.block_hash != data['block_hash']:
            raise ValueError("Block hash does not match!")
        return block

class BlockchainNode:
    def __init__(self, storage_file: str = 'blockchain.json', tx_pool_file: str = 'tx_pool.json'):
        self.storage_file = storage_file
        self.tx_pool_file = tx_pool_file
        self.chain: List[Block] = []
        self.tx_pool: Dict[str, Transaction] = {}  # hash -> transaction
        self.load_chain()
        self.load_tx_pool()

    def create_genesis_block(self) -> Block:
        return Block(
            index=0,
            previous_hash='0',
            station_message='### GENESIS BLOCK OF UVB-76 OBSERVER CHAIN ###',
            tx_hashes=[]
        )

    def load_chain(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.chain = [Block.from_dict(block_data) for block_data in data]
                print(f"Chain loaded. Blocks: {len(self.chain)}")
            except Exception as e:
                print(f"Error loading chain: {e}. Creating new chain.")
                self.chain = [self.create_genesis_block()]
                self.save_chain()
        else:
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def save_chain(self):
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump([block.to_dict() for block in self.chain], f, ensure_ascii=False, indent=2)

    def load_tx_pool(self):
        if os.path.exists(self.tx_pool_file):
            try:
                with open(self.tx_pool_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.tx_pool = {tx_hash: Transaction.from_dict(tx_data) for tx_hash, tx_data in data.items()}
                print(f"Transaction pool loaded. Transactions: {len(self.tx_pool)}")
            except Exception as e:
                print(f"Error loading transaction pool: {e}. Creating new pool.")
                self.tx_pool = {}
        else:
            self.tx_pool = {}

    def save_tx_pool(self):
        with open(self.tx_pool_file, 'w', encoding='utf-8') as f:
            data = {tx_hash: tx.to_dict() for tx_hash, tx in self.tx_pool.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_transaction(self, sender: str, recipient: str, message: str) -> str:
        """Creates a new transaction and adds it to the pool."""
        tx = Transaction(sender, recipient, message)
        self.tx_pool[tx.hash] = tx
        self.save_tx_pool()
        print(f"✅ Transaction created. Hash: {tx.hash[:16]}...")
        return tx.hash

    def add_block(self, station_message: str, selected_tx_hashes: Optional[List[str]] = None):
        """Adds a new block based on the station message and selected transaction hashes."""
        if not station_message.strip():
            print("Station message cannot be empty.")
            return

        if selected_tx_hashes is None:
            # By default, include all unconfirmed transactions from the pool
            selected_tx_hashes = list(self.tx_pool.keys())
        else:
            # Check that all hashes are in the pool
            for h in selected_tx_hashes:
                if h not in self.tx_pool:
                    print(f"Hash {h[:16]}... not in pool. Skipping.")
                    selected_tx_hashes = [h for h in selected_tx_hashes if h in self.tx_pool]

        last_block = self.chain[-1]
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.block_hash,
            station_message=station_message.strip(),
            tx_hashes=selected_tx_hashes
        )
        self.chain.append(new_block)
        self.save_chain()

        # Remove confirmed transactions from the pool
        for h in selected_tx_hashes:
            self.tx_pool.pop(h, None)
        self.save_tx_pool()

        print(f"\n✅ Block #{new_block.index} added!")
        print(f"   Station message: {new_block.station_message}")
        print(f"   Transactions included: {len(new_block.tx_hashes)}")
        print(f"   Block hash: {new_block.block_hash[:16]}...")

    def print_chain(self, limit: Optional[int] = None):
        print("\n" + "="*70)
        print(f"BLOCKCHAIN (total: {len(self.chain)})")
        print("="*70)
        start = 0 if limit is None else max(0, len(self.chain) - limit)
        for i in range(start, len(self.chain)):
            block = self.chain[i]
            print(f"\nBlock #{block.index}")
            print(f"   Prev hash: {block.previous_hash[:16]}...")
            print(f"   Station message: {block.station_message}")
            dt = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   Time: {dt}")
            print(f"   Station message hash: {block.station_message_hash[:16]}...")
            if block.tx_hashes:
                print(f"   Transaction hashes ({len(block.tx_hashes)}):")
                for th in block.tx_hashes[:5]:  # show at most 5
                    print(f"      {th[:16]}...")
                if len(block.tx_hashes) > 5:
                    print(f"      ... and {len(block.tx_hashes)-5} more")
            print(f"   Block hash: {block.block_hash[:16]}...")

    def print_tx_pool(self):
        print("\n--- Unconfirmed transaction pool ---")
        if not self.tx_pool:
            print("Pool is empty.")
        else:
            for tx_hash, tx in self.tx_pool.items():
                dt = datetime.fromtimestamp(tx.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Hash: {tx_hash[:16]}... From: {tx.sender} To: {tx.recipient} Time: {dt}")

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            if curr.previous_hash != prev.block_hash:
                print(f"❌ Link error in block {i}")
                return False
            if curr.block_hash != curr.compute_block_hash():
                print(f"❌ Invalid block hash in block {i}")
                return False
            # Check station message hash
            if curr.station_message_hash != hashlib.sha256(curr.station_message.encode('utf-8')).hexdigest():
                print(f"❌ Invalid station message hash in block {i}")
                return False
        print("✅ Chain is intact.")
        return True

    def sync_with_peer(self, peer_chain_file: str, peer_tx_file: str):
        """Synchronizes the chain and transaction pool with another node's files."""
        # Load peer's chain
        if not os.path.exists(peer_chain_file):
            print(f"File {peer_chain_file} not found.")
            return
        with open(peer_chain_file, 'r', encoding='utf-8') as f:
            peer_chain_data = json.load(f)
        peer_chain = [Block.from_dict(bd) for bd in peer_chain_data]

        # Load peer's pool
        peer_tx_pool = {}
        if os.path.exists(peer_tx_file):
            with open(peer_tx_file, 'r', encoding='utf-8') as f:
                peer_tx_data = json.load(f)
            peer_tx_pool = {h: Transaction.from_dict(txd) for h, txd in peer_tx_data.items()}

        # Compare chains (simple rule: accept longer chain if it starts the same)
        common_len = 0
        for i in range(min(len(self.chain), len(peer_chain))):
            if self.chain[i].block_hash == peer_chain[i].block_hash:
                common_len = i + 1
            else:
                break

        if common_len == 0:
            print("❌ Chains have no common prefix. Synchronization impossible.")
            return

        if len(peer_chain) > len(self.chain) and common_len == len(self.chain):
            print("Our chain is shorter and is a prefix of the peer's chain. Accepting peer's chain.")
            self.chain = peer_chain
            self.save_chain()
        elif len(peer_chain) < len(self.chain) and common_len == len(peer_chain):
            print("Our chain is longer, peer's chain is outdated.")
        elif common_len < len(self.chain) and common_len < len(peer_chain):
            print("⚠️ Conflict: chains have diverged. Manual resolution required.")
            # Could ask the user, but for now do nothing
        else:
            print("Chains are identical.")

        # Merge transaction pools (take all from both pools)
        merged_pool = {**self.tx_pool, **peer_tx_pool}
        if len(merged_pool) != len(self.tx_pool):
            self.tx_pool = merged_pool
            self.save_tx_pool()
            print(f"Transaction pool merged. Now transactions: {len(self.tx_pool)}")
        else:
            print("Transaction pools already synchronized.")

def main():
    print("="*70)
    print("   OFFLINE UVB-76 BLOCKCHAIN WITH MESSAGE SUPPORT")
    print("="*70)
    node = BlockchainNode()

    while True:
        print("\n--- Menu ---")
        print("1. Add new station message (block)")
        print("2. Create personal message (transaction)")
        print("3. Show unconfirmed transaction pool")
        print("4. Show last 10 blocks")
        print("5. Show entire chain")
        print("6. Verify chain integrity")
        print("7. Synchronize with another node (files)")
        print("8. Export transaction pool to file")
        print("9. Import transactions from file")
        print("0. Exit")
        choice = input("Choose action: ").strip()

        if choice == '1':
            msg = input("Enter message from UVB-76: ").strip()
            if msg:
                # Ask which transactions to include
                include_all = input("Include all unconfirmed transactions? (y/n): ").strip().lower()
                if include_all == 'y':
                    node.add_block(msg)
                else:
                    # Show list of hashes in pool
                    node.print_tx_pool()
                    tx_hashes = input("Enter transaction hashes separated by commas (or leave empty): ").strip()
                    if tx_hashes:
                        selected = [h.strip() for h in tx_hashes.split(',') if h.strip()]
                        node.add_block(msg, selected)
                    else:
                        node.add_block(msg, [])
            else:
                print("Empty message.")

        elif choice == '2':
            sender = input("Your name (sender): ").strip()
            recipient = input("To: ").strip()
            message = input("Message text: ").strip()
            if sender and recipient and message:
                node.add_transaction(sender, recipient, message)
            else:
                print("All fields must be filled.")

        elif choice == '3':
            node.print_tx_pool()

        elif choice == '4':
            node.print_chain(limit=10)

        elif choice == '5':
            node.print_chain()

        elif choice == '6':
            node.verify_chain()

        elif choice == '7':
            chain_file = input("Filename of the other node's chain (e.g., peer_chain.json): ").strip()
            tx_file = input("Filename of the other node's transaction pool (e.g., peer_tx.json): ").strip()
            if chain_file and tx_file:
                node.sync_with_peer(chain_file, tx_file)

        elif choice == '8':
            # Export pool to a separate file for transfer
            export_file = input("Filename to export pool: ").strip()
            if export_file:
                with open(export_file, 'w', encoding='utf-8') as f:
                    data = {h: tx.to_dict() for h, tx in node.tx_pool.items()}
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Pool exported to {export_file}")

        elif choice == '9':
            # Import transactions from file (add to pool)
            import_file = input("Filename to import: ").strip()
            if os.path.exists(import_file):
                with open(import_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                imported = 0
                for h, tx_data in data.items():
                    if h not in node.tx_pool:
                        try:
                            tx = Transaction.from_dict(tx_data)
                            node.tx_pool[h] = tx
                            imported += 1
                        except:
                            print(f"Error importing transaction {h[:16]}...")
                node.save_tx_pool()
                print(f"Imported {imported} new transactions.")
            else:
                print("File not found.")

        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid input.")

if __name__ == '__main__':
    main()
