// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0;

contract Arbitration {
    address payable public server;
    uint public percentage;
    mapping(address => uint) public stakes;

    constructor() {
        // copy the first account address from the ganache-cli output and paste below
        server = payable(0x96484e57C41bFfb1bBf51e88Ae5aFD65b1f52f44);
    }

    function stake() external payable {
        require(msg.value > 0, "Must send non-zero amount");
        stakes[msg.sender] += msg.value;
    }

    function resolve_dispute() external {
        uint stakeAmount = stakes[msg.sender];
        require(stakeAmount > 0, "No stake found");

        delete stakes[msg.sender];

        // Send apology to arbitrator and no money to server
        (bool sent, ) = payable(msg.sender).call{value: stakeAmount}("");
        require(sent, "Failed to send apology");

        // Emit event to log the transaction
        emit DisputeResolved(msg.sender, server, stakeAmount);
    }

    function resolve_success() external {
        uint stakeAmount = stakes[msg.sender];
        require(stakeAmount > 0, "No stake found");

        delete stakes[msg.sender];

        // Send the stake money to server
        (bool sent, ) = server.call{value: stakeAmount}("");
        require(sent, "Failed to send money to server");

        // Emit event to log the transaction
        emit SuccessResolved(msg.sender, server, stakeAmount);
    }

    event DisputeResolved(address indexed arbitrator, address indexed server, uint stakeAmount);
    event SuccessResolved(address indexed arbitrator, address indexed server, uint stakeAmount);
}