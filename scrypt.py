import hashlib
import json
import time
import os
from typing import List, Optional, Dict, Any
from datetime import datetime

class Block:
    """Class representing a single block in the chain."""
    def __init__(self, index: int, previous_hash: str, message: str, timestamp: Optional[float] = None):
        self.index = index
        self.previous_hash = previous_hash
        self.message = message
        # If timestamp is not provided, use the current time
        self.timestamp = timestamp if timestamp is not None else time.time()
        # Hash of the message (from the message text in UTF-8 encoding)
        self.message_hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
        # Hash of the entire block (includes previous hash, index, timestamp, message_hash)
        self.block_hash = self.compute_block_hash()

    def compute_block_hash(self) -> str:
        """Computes the SHA-256 hash of the block's content."""
        block_string = json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'message_hash': self.message_hash
        }, sort_keys=True).encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dictionary with block data for serialization."""
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'message': self.message,
            'timestamp': self.timestamp,
            'message_hash': self.message_hash,
            'block_hash': self.block_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Creates a block from a dictionary (deserialization)."""
        block = cls(
            index=data['index'],
            previous_hash=data['previous_hash'],
            message=data['message'],
            timestamp=data['timestamp']
        )
        # Check that the stored hashes match the computed ones (optional)
        if block.message_hash != data['message_hash'] or block.block_hash != data['block_hash']:
            raise ValueError("Block hashes do not match! Data may be corrupted.")
        return block


class BlockchainNode:
    """Blockchain node working completely offline (local storage and input only)."""
    def __init__(self, storage_file: str = 'blockchain.json'):
        self.storage_file = storage_file
        self.chain: List[Block] = []
        self.load_chain()

    def create_genesis_block(self) -> Block:
        """Creates the first (genesis) block with a fixed message."""
        print("Creating genesis block...")
        return Block(
            index=0,
            previous_hash='0',
            message='### GENESIS BLOCK OF UVB-76 OBSERVER CHAIN ###',
            timestamp=time.time()
        )

    def load_chain(self):
        """Loads the chain from a file if it exists. Otherwise creates the genesis block."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.chain = [Block.from_dict(block_data) for block_data in data]
                print(f"Chain loaded from {self.storage_file}. Total blocks: {len(self.chain)}")
            except Exception as e:
                print(f"Error loading chain: {e}. A new chain will be created.")
                self.chain = [self.create_genesis_block()]
                self.save_chain()
        else:
            print("Chain file not found. Creating a new chain.")
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def save_chain(self):
        """Saves the chain to a file in JSON format."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump([block.to_dict() for block in self.chain], f, ensure_ascii=False, indent=2)
        print(f"Chain saved to {self.storage_file}")

    def add_block(self, message: str):
        """Adds a new block with the given message to the chain."""
        if not message.strip():
            print("Empty message cannot be added.")
            return
        last_block = self.chain[-1]
        new_block = Block(
            index=last_block.index + 1,
            previous_hash=last_block.block_hash,
            message=message.strip()
        )
        self.chain.append(new_block)
        self.save_chain()
        print(f"\n✅ Block #{new_block.index} added!")
        print(f"   Message: {new_block.message}")
        print(f"   Message hash: {new_block.message_hash[:16]}...")
        print(f"   Block hash: {new_block.block_hash[:16]}...")

    def print_chain(self, limit: Optional[int] = None):
        """Prints the last few blocks of the chain (or the entire chain)."""
        print("\n" + "="*60)
        print(f"Block chain (total blocks: {len(self.chain)})")
        print("="*60)
        start = 0 if limit is None else max(0, len(self.chain) - limit)
        for i in range(start, len(self.chain)):
            block = self.chain[i]
            print(f"\nBlock #{block.index}")
            print(f"   Previous hash: {block.previous_hash[:16]}...")
            print(f"   Message: {block.message}")
            dt = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   Added at: {dt}")
            print(f"   Message hash: {block.message_hash[:16]}...")
            print(f"   Block hash: {block.block_hash[:16]}...")
        print("="*60)

    def verify_chain(self) -> bool:
        """Verifies chain integrity: all hashes correct and links valid."""
        print("\nVerifying chain integrity...")
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            # Check link to previous block
            if current.previous_hash != previous.block_hash:
                print(f"❌ Error: block #{i} references an incorrect previous hash.")
                return False
            # Check that the stored block hash matches the computed one
            if current.block_hash != current.compute_block_hash():
                print(f"❌ Error: block #{i} hash does not match computed hash.")
                return False
            # Check message hash
            if current.message_hash != hashlib.sha256(current.message.encode('utf-8')).hexdigest():
                print(f"❌ Error: block #{i} message hash does not match.")
                return False
        print("✅ Chain is intact. All blocks are correct.")
        return True

    def sync_with_file(self, other_chain_file: str):
        """
        Synchronizes the current chain with a chain from another file.
        Accepts the longer chain if it starts the same as the current one.
        """
        if not os.path.exists(other_chain_file):
            print(f"File {other_chain_file} not found.")
            return
        try:
            with open(other_chain_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            other_chain = [Block.from_dict(block_data) for block_data in data]
        except Exception as e:
            print(f"Error loading other chain: {e}")
            return

        print(f"\nLoaded other chain from {other_chain_file} (blocks: {len(other_chain)})")

        # Find common prefix
        common_len = 0
        for i in range(min(len(self.chain), len(other_chain))):
            if (self.chain[i].block_hash == other_chain[i].block_hash and
                self.chain[i].message == other_chain[i].message):
                common_len = i + 1
            else:
                break

        if common_len == 0 and len(self.chain) > 0 and len(other_chain) > 0:
            print("❌ Chains do not share a common beginning. Synchronization impossible.")
            return

        if len(other_chain) > len(self.chain) and common_len == len(self.chain):
            # Our chain is a prefix of the longer one — we can extend
            print("Our chain is shorter and fully matches the beginning of the other. Accepting the other chain.")
            self.chain = other_chain
            self.save_chain()
            print("✅ Chain updated.")
        elif len(other_chain) < len(self.chain) and common_len == len(other_chain):
            print("The other chain is shorter and is a prefix of ours. Nothing to do.")
        elif common_len < len(self.chain) and common_len < len(other_chain):
            print(f"⚠️ Conflict: chains diverge at block #{common_len}. Manual resolution required.")
            # Could prompt the user to choose, but for simplicity we do nothing.
        else:
            print("Chains are identical or synchronization not needed.")

def main():
    print("="*60)
    print("   OFFLINE BLOCKCHAIN FOR UVB-76 OBSERVER")
    print("="*60)
    print("Every new message from the radio station becomes a new block.")
    print("The chain is saved in the file blockchain.json.\n")

    node = BlockchainNode()

    while True:
        print("\n--- Menu ---")
        print("1. Add new message (block)")
        print("2. Show last 10 blocks")
        print("3. Show entire chain")
        print("4. Verify chain integrity")
        print("5. Synchronize with another node's file")
        print("6. Exit")
        choice = input("Choose action (1-6): ").strip()

        if choice == '1':
            print("\nEnter the message (e.g., from UVB-76):")
            print("HЖTИ 76472 ПEPEДEPЖKA 4301 8808 Time: 19:44 MSK Date: 2026-03-12")
            message = input("Message: ").strip()
            if message:
                node.add_block(message)
            else:
                print("Message cannot be empty.")
        elif choice == '2':
            node.print_chain(limit=10)
        elif choice == '3':
            node.print_chain()
        elif choice == '4':
            node.verify_chain()
        elif choice == '5':
            filename = input("Enter the filename with the other node's chain (e.g., other.json): ").strip()
            if filename:
                node.sync_with_file(filename)
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid input. Please choose 1-6.")

if __name__ == '__main__':
    main()
