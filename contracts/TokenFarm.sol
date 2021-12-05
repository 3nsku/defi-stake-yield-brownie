// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    //MAPPING: token address -> staker address -> amount
    mapping(address => mapping(address => uint256)) public stakingBalance;
    // this is a counter for the the number of different tokens stacked by each user
    mapping(address => uint256) public uniqueTokensStaked;
    // keep track of the addresses from where to get the lasted price
    mapping(address => address) public tokenToPriceFeed;
    // this is a list all the stakers
    address[] public stakers;
    address[] public allowedTokensAddressList;
    IERC20 public dappToken;

    // stakeTokens
    // unStakeTokens
    // issueTokens
    // addAllowedTokens
    // getValue

    constructor(address _dappTokenAddress) {
        dappToken = IERC20(_dappTokenAddress);
    }

    // Issue reward to users for example for each ETH depositied issue 1 DAPP
    // But if a user has multiple tokes staked (10 ETH and 50 DAI), we need convert everything to eth and the issue an equivalent amount
    // this is a function that issues tokens to all stackers
    function issueTokens() public onlyOwner {
        // loop through all the users
        for (uint256 i; i < stakers.length; i++) {
            address recipient = stakers[i];
            dappToken.transfer(recipient, getUserTotalValue(recipient));
            // issue DAPP Tokens
        }
    }

    function getUserTotalValue(address _user) public view returns (uint256) {
        require(uniqueTokensStaked[_user] > 0, "No tokens Staked!");
        uint256 totalValue = 0;
        for (uint256 k; k < allowedTokensAddressList.length; k++) {
            if (stakingBalance[allowedTokensAddressList[k]][_user] != 0) {
                // then convert the balance to ETH
                totalValue =
                    totalValue +
                    getUserSingleTokenValue(_user, allowedTokensAddressList[k]);
            }
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token)
        public
        view
        returns (uint256)
    {
        // 1 ETH -> return $4500
        // 1 DAI -> reutnr $200
        if (uniqueTokensStaked[_user] <= 0) {
            return 0;
        }

        (uint256 price, uint256 decimals) = getTokenValue(_token);
        // BLANCE 1000000000000000000 WEI -> 1 ETH
        // ETH/USD -> 450000000000
        // 1000000000000000000 * 450000000000 / 10**8
        return (stakingBalance[_token][_user] * price) / (10**decimals);
    }

    function getTokenValue(address _token)
        public
        view
        returns (uint256, uint256)
    {
        // return token value in USD
        address priceFeedAddress = tokenToPriceFeed[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);
    }

    function stakeTokens(uint256 _amount, address _token) public {
        //how much can they stake?
        require(_amount > 0, "Amount must be more than 0"); //you can stake any mount greater than zero
        //what tokens can they stake?
        require(isTokenAllowed(_token), "Token is currently not allowed");

        //transferFrom
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);

        //check if first time staking
        if (uniqueTokensStaked[msg.sender] == 0) {
            stakers.push(msg.sender);
        }
        updateUniqueTokensStaked(msg.sender, _token);
        //update mapping
        stakingBalance[_token][msg.sender] =
            stakingBalance[_token][msg.sender] +
            _amount;
    }

    function unStakeTokens(address _token) public {
        uint256 stakeBalance = stakingBalance[_token][msg.sender];
        require(stakeBalance > 0, "No Tokens To Unstake");
        //transfer from smart contarct all the staked token.
        //update mapping
        stakingBalance[_token][msg.sender] = 0;
        IERC20(_token).transfer(msg.sender, stakeBalance);
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    //this is a function that checks if the sender address has any tokens staked. if not this means that he is a new user
    function updateUniqueTokensStaked(address _user, address _token) internal {
        //check if staker address inside mapping
        if (stakingBalance[_token][_user] <= 0) {
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
        }
    }

    // this is a function that adds a new token to the allowed list of tokens. Only the admin can call this function
    function addAllowedToken(address _token) public onlyOwner {
        allowedTokensAddressList.push(_token);
    }

    function setPriceFeedContract(address _token, address _priceFeed)
        public
        onlyOwner
    {
        tokenToPriceFeed[_token] = _priceFeed;
    }

    // this is a function that checks if the token address is inside the list of allowed tokens
    function isTokenAllowed(address _token) public view returns (bool) {
        for (uint256 j = 0; j < allowedTokensAddressList.length; j++) {
            if (allowedTokensAddressList[j] == _token) {
                return true;
            }
        }
        return false;
    }
}
