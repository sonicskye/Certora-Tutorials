methods {
    getPointsOfContender(address) returns (uint256) envfree => DISPATCHER(false)
    hasVoted(address) returns (bool) envfree => DISPATCHER(false)
    getWinner() returns (address, uint256) envfree => DISPATCHER(false)
    getFullVoterDetails(address) returns (uint8, bool, bool, uint256, bool) envfree => DISPATCHER(false)
    getFullContenderDetails(address) returns (uint8, bool, uint256) envfree => DISPATCHER(false)
    //registerVoter(uint8) returns (bool) envfree => DISPATCHER(false)
}