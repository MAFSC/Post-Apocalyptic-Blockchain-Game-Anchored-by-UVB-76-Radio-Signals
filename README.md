# Post-Apocalyptic-Blockchain-Game-Anchored-by-UVB-76-Radio-Signals
The Idea

Imagine a world without internet. No TCP/IP, no peers, no mining pools. Only a crackling shortwave radio and the occasional voice message from a station that has been buzzing since the Soviet era.
What if we build a blockchain where each new block is created only when UVB-76 transmits a voice message? Every participant listens to the same radio, records the message, hashes it, and appends a new block to their local chain. The radio becomes a global, immutable clock and a source of randomness.

Later, we add a second layer: personal messages between users. These messages are not broadcast – they are exchanged offline (via USB sticks, Bluetooth, even paper). But their hashes can be embedded into the next UVB-76 block, forever proving that the message existed at that moment. The radio anchors the human conversation into an unforgeable timeline.

It’s a post‑apocalyptic game, a crypto‑archaeological artifact, and a meditation on trust without infrastructure.
How it works (in short)

    Layer 1 – The Anchor Chain
    Every time UVB-76 speaks (e.g., "MЯСНИК 45 39 72 ЗИМОРОДОК"), participants create a new block containing that message, its hash, and a list of user‑message hashes. The block is chained to the previous one via the usual previous_hash.

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

    Run it: python scrypt.py.

    Listen to UVB‑76 online at https://www.uvb76radio.ru/ or https://t.me/s/uvb76broadcast or https://web.max.ru/-71006372263282 or via a real shortwave receiver (4625 kHz).

    Every time you hear a voice message, add it as a new block.

    Exchange your blockchain.json and tx_pool.json files with other players (by email, Telegram, or in person) to synchronize.

The game is open – there is no central authority. The chain grows with every transmission.
