# Image Deduplication in Cloud Storage using Cryptographic Techniques

## Overview
Cloud storage systems often waste space and energy by storing multiple copies of the same image, especially when users upload slightly transformed versions (resized, filtered, or cropped). Traditional hashing methods fail to detect near-duplicates and lack privacy guarantees.

This project presents a secure, cryptography-backed image deduplication framework that detects and eliminates redundant image uploads while maintaining fairness, transparency, and ownership integrity through blockchain and zero-knowledge proofs.

---

## Problem Statement
Cloud Service Providers (CSPs) face:
- Storage inefficiency due to redundant or transformed images.
- Ownership disputes over copyrighted content.
- Security risks when storing unverified or duplicated data.

Our goal is to design a privacy-preserving deduplication system that:
1. Detects exact and near-duplicate images.
2. Verifies copyright and transformation authenticity.
3. Resolves disputes fairly via cryptographic proofs and blockchain.

---

## System Design

### 1. Deduplication Workflow
- **Ownership Verification:**  
  RSA digital signatures embedded in image EXIF metadata confirm ownership.
- **Compression and Hashing:**  
  Images are compressed using SPIHT (Set Partitioning in Hierarchical Trees) to extract wavelet coefficients.  
  A Wavelet Hash (wHash) computes a locality-sensitive binary fingerprint.
- **Similarity Comparison:**  
  Hamming distance between hashes determines image similarity; near-duplicates trigger transformation verification.

### 2. Transformation Verification
- Each image transformation (crop, blur, resize, etc.) is logged and committed cryptographically using the Pedersen Commitment Scheme.  
- The system verifies the commitment to ensure authenticity before accepting a modified image.

### 3. Blockchain Integration
- All upload transactions and transformations are stored on an Ethereum-based blockchain (via smart contracts in Solidity).
- Incentivization model:
  - Original uploader earns a micro-fee when others upload transformed copies.
  - Unverified or duplicate uploads are automatically rejected.

### 4. Arbitration Module
- Users can dispute a rejected upload by staking tokens.
- A Zero-Knowledge SNARK proof (generated with ZoKrates) verifies that the server correctly identified an existing duplicate.
- If successful, the user regains their stake and ownership is updated.

---

## Implementation

| Component | Technology Used |
|------------|----------------|
| Web Backend | Python Flask |
| Frontend | HTML, JS, Bootstrap |
| Blockchain | Solidity (Ethereum, Ganache) |
| Cryptography | RSA, Pedersen Commitments, ZK-SNARKs |
| Image Processing | SPIHT Compression, Wavelet Hashing |
| Proof Engine | ZoKrates (Rust-based toolkit) |

System workflows include:
- Upload Validation
- Transformation Commitment
- Arbitration and Proof Generation

---

## Evaluation

| Metric | Result |
|--------|---------|
| Dataset Size | 150 images |
| Average Storage Savings | 34.77% |
| SPIHT Compression Time | Grows linearly with image matrix size |
| Blockchain Proof Latency | Negligible in small private network |
| Security | Guarantees non-repudiation, fairness, and proof of originality |

---

## Results Summary
- Reduced redundant storage by approximately 35% while ensuring verifiable ownership.
- Introduced an on-chain arbitration mechanism for fairness.
- Demonstrated scalability through modular architecture and efficient hash computation.

---

## Future Work
- Extend deduplication to encrypted images (using message-locked encryption).  
- Broaden transformation log formats to support complex edits.  
- Introduce dynamic pricing models for storage and arbitration fairness.

---

## Contributors
- Adarsh Ashokan  
- Arnav Menon R  
- Ashwath Niranjh A  
Department of Computer Science and Engineering,  
National Institute of Technology, Trichy (2023)
