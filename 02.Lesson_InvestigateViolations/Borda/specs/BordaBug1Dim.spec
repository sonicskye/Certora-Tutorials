/*
CVL for BordaBug1.sol
Each rule must have assertion at the end.
*/

import "methods/Borda.spec"

// https://docs.certora.com/en/latest/docs/confluence/anatomy/hooks.html?highlight=hook
/*definition ContendersStruct_age(uint256 s) returns uint256 =
    s & 0xff;
definition ContendersStruct_registered(uint256 s) returns uint256 =
    (s & 0xff00) >>> 2 ^ 1;
definition ContendersStruct_points(uint256 s) returns uint256 =
    (s & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000) >>> 2 ^ 2;
*/

///// contenders ghost and hooks /////

ghost mapping(address => uint8) gContendersAge; // 1 byte
ghost mapping(address => bool) gContendersRegistered; // 1 byte
ghost mapping(address => uint256) gContendersPoints; // 32 bytes

hook Sstore _contenders[KEY address contender].(offset 0) uint8 age STORAGE {
    havoc gContendersAge assuming gContendersAge@new[contender] == age;
}

hook Sload uint8 age _contenders[KEY address contender].(offset 0) STORAGE {
    require gContendersAge[contender] == age;
}

hook Sstore _contenders[KEY address contender].(offset 1) bool registered STORAGE {
    havoc gContendersRegistered assuming gContendersRegistered@new[contender] == registered;
} 

hook Sload bool registered _contenders[KEY address contender].(offset 1) STORAGE {
    require gContendersRegistered[contender] == registered;
}

hook Sstore _contenders[KEY address contender].(offset 32) uint256 points (uint256 oldPoints) STORAGE {
    havoc gContendersPoints assuming gContendersPoints@new[contender] == points;
    //havoc gContendersPoints assuming gContendersPoints@new[contender] == oldPoints + 3;
    //gContendersPoints[contender] = points;
}

hook Sload uint256 points _contenders[KEY address contender].(offset 32) STORAGE {
    require gContendersPoints[contender] == points;
    //gContendersPoints[contender] = points;
}

///// voters ghost and hooks /////

ghost mapping(address => uint8) gVotersAge; // 1 bytes
ghost mapping(address => bool) gVotersRegistered; // 1 byte
ghost mapping(address => bool) gVotersVoted; // 1 byte
ghost mapping(address => uint256) gVotersAttempts; // 32 bytes
ghost mapping(address => bool) gVotersBlackListed;  // 1 byte
// We use two ghosts to handle an array _blackList
// One to store the key-value pairs and another to store the length
ghost mapping(uint256 => address) gBlackListArr;
ghost uint256 gBlackListArrLength;

hook Sstore _voters[KEY address voter].(offset 0) uint8 age STORAGE {
    havoc gVotersAge assuming gVotersAge@new[voter] == age;
}

hook Sload uint8 age _voters[KEY address voter].(offset 0) STORAGE {
    require gVotersAge[voter] == age;
}

hook Sstore _voters[KEY address voter].(offset 1) bool registered STORAGE {
    havoc gVotersRegistered assuming gVotersRegistered@new[voter] == registered;
}

hook Sload bool registered _voters[KEY address voter].(offset 1) STORAGE {
    require gVotersRegistered[voter] == registered;
}

hook Sstore _voters[KEY address voter].(offset 2) bool voted STORAGE {
    havoc gVotersVoted assuming gVotersVoted@new[voter] == voted;
}

hook Sload bool voted _voters[KEY address voter].(offset 2) STORAGE {
    require gVotersVoted[voter] == voted;
}

hook Sstore _voters[KEY address voter].(offset 32) uint256 attempts STORAGE {
    havoc gVotersAttempts assuming gVotersAttempts@new[voter] == attempts;
}

hook Sload uint256 attempts _voters[KEY address voter].(offset 32) STORAGE {
    require gVotersAttempts[voter] == attempts;
}

hook Sstore _voters[KEY address voter].(offset 64) bool blackListed STORAGE {
    havoc gVotersBlackListed assuming gVotersBlackListed@new[voter] == blackListed;
}

hook Sload bool blackListed _voters[KEY address voter].(offset 64) STORAGE {
    require gVotersBlackListed[voter] == blackListed;
}

hook Sstore _blackList[INDEX uint256 i] address voter STORAGE {
    havoc gBlackListArr assuming gBlackListArr@new[i] == voter;
}

hook Sload address voter _blackList[INDEX uint256 i] STORAGE {
    require gBlackListArr[i] == voter;
}

// https://docs.certora.com/en/latest/docs/confluence/map/ghosts.html?highlight=ghost%20array#verification-with-ghosts
// This is because Solidity storage stores the length of the array in the array slot
// We use slot number here. TODO: check if it is correct.
hook Sstore (slot 1) uint256 lenNew STORAGE {
    gBlackListArrLength = lenNew;
}

///// pointsOfWinner ghost and hooks /////

ghost uint256 gPointsOfWinner;

hook Sstore pointsOfWinner uint256 points STORAGE {
    havoc gPointsOfWinner assuming gPointsOfWinner@new == points;
}

hook Sload uint256 points pointsOfWinner STORAGE {
    require gPointsOfWinner == points;
}


///////////////////////////////////////////////////////////////////////
// Rules
///////////////////////////////////////////////////////////////////////


rule registerVoter {
    env e;
    uint8 age;
    address voter = e.msg.sender;

    uint8 voter_details_age;
    bool voter_details_registered;
    bool voter_details_registered_before;
    bool voter_details_voted;
    uint256 voter_details_attempts;
    bool voter_details_blacklisted;

    _, voter_details_registered_before, _, _, _ = getFullVoterDetails(voter);

    // Requirements
    require(voter_details_registered_before == false);

    registerVoter(e, age);

    voter_details_age, voter_details_registered, voter_details_voted, voter_details_attempts, voter_details_blacklisted = getFullVoterDetails(voter);

    assert hasVoted(voter) == false, "Voter not registered";

    assert voter_details_attempts == 0, "Voter should not have any attempts";
    assert voter_details_blacklisted == false, "Voter should not be blacklisted";

    assert gVotersAge[voter] == age, "Voter age not set";
    assert gVotersRegistered[voter] == true, "Voter should be registered";
    assert gVotersAttempts[voter] == 0, "Voter should not have any attempts";
    assert gVotersBlackListed[voter] == false, "Voter should not be blacklisted";
}


rule registerContender {
    env e;
    uint8 age;
    address contender = e.msg.sender;

    // Requirements
    require(gContendersRegistered[contender] == false);

    uint8 contender_details_age;
    bool contender_details_registered;
    uint256 contender_details_points;
    contender_details_age, contender_details_registered, contender_details_points = getFullContenderDetails(contender);

    require(contender_details_age == 0);
    require(contender_details_registered == false);
    require(contender_details_points == 0);
    require(gContendersPoints[contender] == 0);
    
    assert gContendersAge[contender] == 0, "Contender age should not be set";
    assert gContendersRegistered[contender] == false, "Contender should not be registered";
    assert gContendersPoints[contender] == 0, "Contender points not set";

    registerContender(e, age);

    assert gContendersAge[contender] == age, "Contender age not set";
    assert gContendersRegistered[contender] == true, "Contender not registered";
    assert gContendersPoints[contender] == 0, "Contender points should not be set";

}

rule vote {
    env e;
    address voter = e.msg.sender;
    uint256 points = 3;
    address first;
    address second;
    address third;

    uint8 voter_details_age;
    bool voter_details_registered;
    bool voter_details_voted;
    uint256 voter_details_attempts;
    bool voter_details_blacklisted;

    uint8 contender_details_age_first;
    bool contender_details_registered_first;
    uint256 contender_details_points_first_before;
    uint256 contender_details_points_first_after;
    uint8 contender_details_age_second;
    bool contender_details_registered_second;
    uint256 contender_details_points_second_before;
    uint256 contender_details_points_second_after;
    uint8 contender_details_age_third;
    bool contender_details_registered_third;
    uint256 contender_details_points_third_before;
    uint256 contender_details_points_third_after;


    voter_details_age, voter_details_registered, voter_details_voted, voter_details_attempts, voter_details_blacklisted = getFullVoterDetails(voter);
    contender_details_age_first, contender_details_registered_first, contender_details_points_first_before = getFullContenderDetails(first);
    contender_details_age_second, contender_details_registered_second, contender_details_points_second_before = getFullContenderDetails(second);
    contender_details_age_third, contender_details_registered_third, contender_details_points_third_before = getFullContenderDetails(third);

    // Requirements
    require(voter_details_registered == true);
    require(gVotersRegistered[voter] == true);
    require(voter_details_blacklisted == false);
    require(gVotersBlackListed[voter] == false);

    require(contender_details_registered_first == true);
    require(contender_details_registered_second == true);
    require(contender_details_registered_third == true);
    require(gContendersRegistered[first] == true);
    require(gContendersRegistered[second] == true);
    require(gContendersRegistered[third] == true);
    require(first != second);
    require(first != third);
    require(second != third);
    /*
    require(contender_details_points_first_before == 0);
    require(contender_details_points_second_before == 0);
    require(contender_details_points_third_before == 0);
    require(gContendersPoints[first] == 0);
    require(gContendersPoints[second] == 0);
    require(gContendersPoints[third] == 0);
    */

    // Action
    vote(e, first, second, third);

    _, _, contender_details_points_first_after = getFullContenderDetails(first);
    _, _, contender_details_points_second_after = getFullContenderDetails(second);
    _, _, contender_details_points_third_after = getFullContenderDetails(third);

    // Assertions
    assert contender_details_points_first_after == contender_details_points_first_before + points, "First Contender points not properly updated";
    assert contender_details_points_second_after == contender_details_points_second_before + points, "Second Contender points not properly updated";
    assert contender_details_points_third_after == contender_details_points_third_before + points, "Third Contender points not properly updated";
    assert gContendersPoints[first] == contender_details_points_first_after, "First gContender points not properly updated";
    assert gContendersPoints[second] == contender_details_points_second_after, "Second gContender points not properly updated";
    assert gContendersPoints[third] == contender_details_points_third_after, "Third gContender points not properly updated";

    uint256 pointsOfWinner;
    address winner;
    winner, pointsOfWinner = getWinner();

    assert pointsOfWinner >= contender_details_points_first_after, "Winner points not properly updated";
    assert pointsOfWinner >= contender_details_points_second_after, "Winner points not properly updated";
    assert pointsOfWinner >= contender_details_points_third_after, "Winner points not properly updated";


}

rule get_points_of_contender {
    env e;
    address contender;

    method f;
    calldataarg args;

    f(e, args);

    assert getPointsOfContender(contender) == gContendersPoints[contender], "getPointsOfContender() should return the same as gContendersPoints[contender]";

}

rule has_voted {
    env e;
    address voter;// = e.msg.sender;
    address first;
    address second;
    address third;

    vote(e, first, second, third);

    method f;
    calldataarg args;

    f(e, args);

    assert hasVoted(voter) == gVotersVoted[voter], "hasVoted() should return the same as gVotersVoted[voter]";

}

rule get_winner {
    env e;

    method f;
    calldataarg args;

    f(e, args);

    uint256 pointsOfWinner;
    address winner;
    winner, pointsOfWinner = getWinner();

    assert pointsOfWinner == gPointsOfWinner, "pointsOfWinner should be the same as gPointsOfWinner";
}


rule voter_not_registered {
    env e;
    address voter = e.msg.sender;
    address first;
    address second;
    address third;

    // Requirements
    require(gVotersRegistered[voter] == false);

    // Action
    vote@withrevert(e, first, second, third);

    bool success =! lastReverted;

    assert success == false, "Voter not registered should not be able to vote";
}

// This rule is VIOLATED
// This indicates that blacklisted voters are able to vote
rule voter_blacklisted {
    env e;
    address voter = e.msg.sender;
    address first;
    address second;
    address third;

    // Requirements
    require(gVotersBlackListed[voter] == true);

    // Action
    vote@withrevert(e, first, second, third);

    bool success =! lastReverted;

    assert success == false, "Voter blacklisted should not be able to vote";
}


rule vote_blacklist {
    env e;
    address voter = e.msg.sender;
    address first;
    address second;
    address third;

    require(gVotersBlackListed[voter] == true);
    require(gVotersVoted[voter] == true);
    require(gVotersAttempts[voter] >= 3);

    vote@withrevert(e, first, second, third);

    bool success =! lastReverted;

    assert gBlackListArrLength > 0, "Blacklist array length should be greater than 0";

    assert success == false, "Voted voter should not be able to vote";

    

}