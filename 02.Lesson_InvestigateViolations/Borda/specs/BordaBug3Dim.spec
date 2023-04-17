/*
CVL For BordaBug2.sol
*/

import "methods/Borda.spec"

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


rule vote {
    // max_uint256 is a keyword, so we do not need to declare it
    //uint256 max_uint256 = 2^256 - 1; // 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    env e;
    address voter = e.msg.sender;
    uint256 points_1 = 3;
    uint256 points_2 = 2;
    uint256 points_3 = 1;
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
    //require(gVotersRegistered[voter] == true);
    require(voter_details_blacklisted == false);
    //require(gVotersBlackListed[voter] == false);

    require(contender_details_registered_first == true);
    require(contender_details_registered_second == true);
    require(contender_details_registered_third == true);
    //require(gContendersRegistered[first] == true);
    //require(gContendersRegistered[second] == true);
    //require(gContendersRegistered[third] == true);
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
    // To avoid overflow, we ensure the points before is less than max_uint256 - points
    require(max_uint256 - points_1 >= contender_details_points_first_before);
    require(max_uint256 - points_2 >= contender_details_points_second_before);
    require(max_uint256 - points_3 >= contender_details_points_third_before);

    // Action
    vote(e, first, second, third);

    _, _, contender_details_points_first_after = getFullContenderDetails(first);
    _, _, contender_details_points_second_after = getFullContenderDetails(second);
    _, _, contender_details_points_third_after = getFullContenderDetails(third);

    // Assertions
    assert contender_details_points_first_after == contender_details_points_first_before + points_1, "First Contender points not properly updated";
    assert contender_details_points_second_after == contender_details_points_second_before + points_2, "Second Contender points not properly updated";
    assert contender_details_points_third_after == contender_details_points_third_before + points_3, "Third Contender points not properly updated";
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