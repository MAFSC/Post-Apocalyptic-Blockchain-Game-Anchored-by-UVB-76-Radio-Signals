# Post-Apocalyptic-Blockchain-Game-Anchored-by-UVB-76-Radio-Signals
The Idea

Imagine a world without internet. No TCP/IP, no peers, no mining pools. Only a crackling shortwave radio and the occasional voice message from a station that has been buzzing since the Soviet era.
What if we build a blockchain where each new block is created only when UVB-76 transmits a voice message? Every participant listens to the same radio, records the message, hashes it, and appends a new block to their local chain. The radio becomes a global, immutable clock and a source of randomness.

Later, we add a second layer: personal messages between users. These messages are not broadcast – they are exchanged offline (via USB sticks, Bluetooth, even paper). But their hashes can be embedded into the next UVB-76 block, forever proving that the message existed at that moment. The radio anchors the human conversation into an unforgeable timeline.

It’s a post‑apocalyptic game, a crypto‑archaeological artifact, and a meditation on trust without infrastructure.
How it works (in short)

    Layer 1 – The Anchor Chain
    Every time UVB-76 speaks (e.g., "HЖTИ 76472 ПEPEДEPЖKA 4301 8808"), participants create a new block containing that message, its hash, and a list of user‑message hashes. The block is chained to the previous one via the usual previous_hash.

    Layer 2 – User Messages
    Anyone can create a transaction (sender, recipient, text). Transactions are stored in a local pool and can be exchanged physically. When the next radio message arrives, the participant may include any set of transaction hashes into the new block. Once included, the transaction is permanently anchored.

    Consensus?
    There is no global consensus in the usual sense – because there is no network. Instead, when two participants meet, they compare their chains and merge them using a simple rule: accept the longer chain if it starts with the same genesis. Conflicts are resolved manually (or by trusting a known “official” log posted later on the UVB-76 website).

Why “post‑apocalyptic”?

Because this blockchain works without any online communication. The only global broadcast is the radio. Everyone is an isolated node, and synchronization happens only when people physically meet. It’s a perfect fit for a role‑playing game set in a world after the collapse of the internet.
The First Client (Python)

Below is a complete Python script that implements both layers. It saves everything in JSON files, so you can easily exchange data with other players.

How to join the game

    Install Python 3.6+.

    Save the script as scrypt.py.

    Run it: python3 scrypt.py.

    Listen to UVB‑76 online at https://www.uvb76radio.ru/ or https://t.me/s/uvb76broadcast or https://web.max.ru/-71006372263282 or via a real shortwave receiver (4625 kHz).

    Every time you hear a voice message, add it as a new block.

    Exchange your blockchain.json and tx_pool.json files with other players (by email, Telegram, or in person) to synchronize.

📝 Complete Guide: Send and Verify a Message
🔰 Step 0: First Run

On first run, the genesis block is automatically created from a real UVB-76 message:
text

HЖTИ 76472 ПEPEДEPЖKA 4301 8808

This ensures all participants start from the same block.
📤 Step 1: Create a Message (Sender)

    Run the script:

bash

python3 uvb76_node.py

    Select option 2 (Create personal message):

text

Choose action: 2

    Enter the details:

text

Your name (sender): Tom
To: Jerry
Message text: Hello, this is a test message!

    The script will show the message hash:

text

✅ Transaction created successfully!
   Hash: 71fb2769a2b91f4d2296059d48ae9a08836e479fed1ecfce36ce3925d0779d5f

    IMPORTANT: Save this message to a file. The most reliable way:

        Select option 9 (Export transaction pool to file)

        Enter a filename, e.g., tom_to_jerry.json

        The script will create a JSON file with all your unconfirmed transactions

📨 Step 2: Transfer the Message (Sender)

Send the file tom_to_jerry.json to the recipient using any method:

    Via messenger (Telegram, WhatsApp)

    By email

    Via USB flash drive

    Via Bluetooth

    Print a QR code with the file contents

📥 Step 3: Receive the Message (Recipient)

    Copy the received file (e.g., tom_to_jerry.json) to the same folder as the script.

    Run the script and select option 10 (Import transactions):

text

Choose action: 10
Import filename: tom_to_jerry.json

    The script will show the import result:

text

✅ Import complete: Imported: 1, Total in pool now: 1

🔍 Step 4: Verify the Message (Recipient)

    Select option 4 (Decrypt/show message by hash):

text

Choose action: 4
Enter transaction hash: 71fb2769a2b91f4d2296059d48ae9a08836e479fed1ecfce36ce3925d0779d5f

    The script will find the message and display:

text

======================================================================
🔍 SEARCH RESULTS FOR HASH: 71fb2769a2b91f4d...
======================================================================
✅ Found in: file: tom_to_jerry.json

📨 MESSAGE DETAILS:
   ┌─────────────────────────────────
   │ From:      Tom
   │ To:        Jerry
   │ Message:   Hello, this is a test message!
   │ Timestamp: 2026-03-19 15:30:45
   │ Full hash: 71fb2769a2b91f4d...
   └─────────────────────────────────

⛓️ Step 5: Anchor the Message in the Blockchain (Both Participants)

When UVB-76 transmits a new message (listen online at https://www.uvb76radio.ru/):

    Both participants (sender and recipient) must add a new block:

text

Choose action: 1
Enter message from UVB-76: БРОНЯ 00 19 85 АКУЛА
Include all unconfirmed transactions? (y/n): y

    The "Tom→Jerry" message hash will be included in the new block:

text

✅ Block #3 added!
   Station message: БРОНЯ 00 19 85 АКУЛА
   Transactions included: 1
   Block hash: a7d3f8e2c1b5...

🔄 Step 6: Synchronize When Meeting

When participants meet in person, they can synchronize their blockchains:

    One participant exports their chain (option 8 is used for synchronization, but actually the chain files are already there - blockchain.json and tx_pool.json)

    Copy the files to each other

    Each performs synchronization:

text

Choose action: 8
Peer's chain filename: peer_blockchain.json
Peer's transaction pool filename: peer_tx.json

💡 Important Tips

    Save all JSON files with transactions in a separate folder. Even after confirmation in the blockchain, the actual messages are only stored in these files.

    Name files by hash for convenience: 71fb2769...d5f.json

    Regularly backup the script folder

    Check the genesis block when synchronizing with new participants

    Listen to UVB-76 online: https://www.uvb76radio.ru/

📁 File Structure

    uvb76_node.py - the main script

    blockchain.json - your local blockchain

    tx_pool.json - unconfirmed transactions

    *.json - exported transaction files (share these!)

⚠️ Common Issues and Solutions
Problem	Solution
"Transaction not found"	Make sure the JSON file with the transaction is in the same folder
Genesis block mismatch	Delete blockchain.json and restart - it will recreate with correct genesis
Can't find file by hash	Rename your file to <hash>.json exactly
Synchronization fails	Check that genesis blocks match (same station message)
🎯 Summary

This system allows you to:

    ✅ Send private messages that are anchored to real radio transmissions

    ✅ Verify messages by their hash

    ✅ Build an immutable history of communications

    ✅ Participate in a post-apocalyptic blockchain game

Join us! Create your first message and share it with another participant. The blockchain grows with every UVB-76 transmission.





