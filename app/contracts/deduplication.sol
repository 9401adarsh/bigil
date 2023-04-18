// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

contract ImageTransformations {
    struct Transformation {
        string log;
        address ownerAddress;
        string imageId;
    }
    
    string public message;

    mapping(string => Transformation) public transformations;
    
    address payable public serverAddress;
    
    event TransformationLogged(string indexed imageId, string log, address ownerAddress, uint256 amountSent);
    
    constructor() {
        message = "Hello, World!";
        // copy the first account address from the ganache-cli output and paste below
        serverAddress = payable(0x098224edd0c93A3Cdd6988a80d4681Ef0E3976ed);
    }
    
    function greet() public view returns (string memory){
        return message;
    }
    function logTransformation(string memory _log, address _ownerAddress, string memory _imageId) public payable {
        require(msg.value > 0, "You must send some currency to log a transformation.");
        
        uint256 amountToSend = msg.value;
        uint256 serverCut = amountToSend / 2; // Send 50% of the value to the server
        uint256 ownerCut = amountToSend - serverCut; // Send the rest to the owner
        
        (bool success,) = serverAddress.call{value: serverCut}("");
        require(success, "Failed to send funds to server address.");
        
        (bool ownerSuccess,) = _ownerAddress.call{value: ownerCut}("");
        require(ownerSuccess, "Failed to send funds to owner address.");
        
        transformations[_imageId] = Transformation(_log, _ownerAddress, _imageId);
        
        emit TransformationLogged(_imageId, _log, _ownerAddress, ownerCut);
    }
}
