/*
CVL for ERC20
There are some errors on sumOfBalances() and noChangeTotalSupply()
I think they are because of deposit() and withdraw() methods

*/

import "methods/IERC20.spec"

rule mint {
    env e;
    address owner = _owner(e);
    address random_minter;
    address receiver;
    uint256 amount;

    // Require
    require(e.msg.sender != owner);
    require(amount > 0);

    mathint balance_before = balanceOf(receiver);
    mathint total_supply_before = totalSupply();

    // Minting is only allowed for the owner
    // But the prover doesn't seem to care about this
    mint(e, receiver, amount);

    mathint balance_after = balanceOf(receiver);
    mathint total_supply_after = totalSupply();

    assert balance_after == balance_before + amount;
    assert total_supply_after == total_supply_before + amount;

    //assert (amount > 0 && e.msg.sender == owner) => total_supply_after > 0, "minting failed";
    //assert (amount > 0) => total_supply_after > 0, "minting failed";
    assert total_supply_after > 0, "minting failed";
}

rule mintRevert {
    env e;
    address owner = _owner(e);
    address receiver;
    uint256 amount;

    // Require
    require(e.msg.sender != owner);
    require(amount > 0);


    mint@withrevert(e, receiver, amount);

    assert lastReverted,
        "Minting must be done by the owner";
}


// From https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/certora/specs/ERC20.spec

// This ghost is a function
ghost sumOfBalances() returns uint256 {
  init_state axiom sumOfBalances() == 0;
}

// We use new() and old() because we use ghost function
hook Sstore _balances[KEY address addr] uint256 newValue (uint256 oldValue) STORAGE {
    havoc sumOfBalances assuming sumOfBalances@new() == sumOfBalances@old() + newValue - oldValue;
}

// This ghost is a variable
ghost uint256 gTotalSupply;

// Note there is no new() and old() here
// We use hook to access the _totalSupply storage
hook Sstore _totalSupply uint256 newValue (uint256 oldValue) STORAGE {
    havoc gTotalSupply assuming gTotalSupply@new == newValue;
}

invariant totalSupplyIsSumOfBalances()
    totalSupply() == sumOfBalances()

invariant totalSupplyIsTotalSupply()
    totalSupply() == gTotalSupply


rule noChangeTotalSupply(env e) {
    requireInvariant totalSupplyIsSumOfBalances();
    requireInvariant totalSupplyIsTotalSupply();

    method f;
    calldataarg args;

    uint256 totalSupplyBefore = totalSupply();
    f(e, args);
    uint256 totalSupplyAfter = totalSupply();

    assert totalSupplyAfter > totalSupplyBefore => f.selector == mint(address,uint256).selector;
    assert totalSupplyAfter < totalSupplyBefore => f.selector == burn(address,uint256).selector;
    //assert totalSupplyAfter > totalSupplyBefore => f.selector == deposit().selector;
    //assert totalSupplyAfter < totalSupplyBefore => f.selector == withdraw(uint256).selector;
}



rule transfer {
    env e;
    address recipient;
    uint256 amount;

    mathint sender_balance_before = balanceOf(e.msg.sender);
    mathint recipient_balance_before = balanceOf(recipient);
    mathint total_supply_before = totalSupply();

    // To ensure that the asserts hold, we must have this condition
    require(e.msg.sender != recipient);

    transfer(e, recipient, amount);

    mathint sender_balance_after = balanceOf(e.msg.sender);
    mathint recipient_balance_after = balanceOf(recipient);
    mathint total_supply_after = totalSupply();

    assert sender_balance_after == sender_balance_before - amount, "Amount must be correctly taken from the sender";
    assert recipient_balance_after == recipient_balance_before + amount, "Amount must be transferred correctly to the recipient";
    assert total_supply_after == total_supply_before, "Total supply should not change";
}

// https://docs.certora.com/en/latest/docs/confluence/anatomy/update.html?highlight=mapping%20of%20mappings
ghost mapping(address => mapping(address => uint256)) gallowances;


// https://docs.certora.com/en/latest/docs/confluence/anatomy/hooks.html?highlight=hook
hook Sstore _allowances[KEY address owner][KEY address spender] uint256 newValue (uint256 oldValue) STORAGE {
    havoc gallowances assuming gallowances@new[owner][spender] == newValue;
}

rule approve {
    requireInvariant totalSupplyIsSumOfBalances();

    env e;
    address spender;
    uint256 amount;

    mathint allowance_before = allowance(e.msg.sender, spender);

    approve(e, spender, amount);

    mathint allowance_after = allowance(e.msg.sender, spender);

    assert allowance_after == amount, "Allowance must be set correctly";
    assert gallowances[e.msg.sender][spender] == amount, "Allowance must be set correctly";
}

rule transferFrom {
    env e;
    address sender;
    address recipient;
    uint256 amount;

    // Requirements
    require(sender != recipient);
    require(e.msg.sender != sender);
    require(amount > 0); // We make sure that the condition holds when amount is more than zero

    mathint sender_balance_before = balanceOf(sender);
    mathint recipient_balance_before = balanceOf(recipient);
    mathint total_supply_before = totalSupply();
    mathint allowance_before = allowance(sender, e.msg.sender);

    transferFrom(e, sender, recipient, amount);

    mathint sender_balance_after = balanceOf(sender);
    mathint recipient_balance_after = balanceOf(recipient);
    mathint total_supply_after = totalSupply();
    mathint allowance_after = allowance(sender, e.msg.sender);

    assert sender_balance_after == sender_balance_before - amount, "Amount must be correctly taken from the sender";
    assert recipient_balance_after == recipient_balance_before + amount, "Amount must be transferred correctly to the recipient";
    assert total_supply_after == total_supply_before, "Total supply should not change";
    assert allowance_after == allowance_before - amount, "Allowance must be correctly updated";
    
}

rule increaseAllowance {
    env e;
    address spender;
    uint256 addedValue;

    mathint allowance_before = allowance(e.msg.sender, spender);

    increaseAllowance(e, spender, addedValue);

    mathint allowance_after = allowance(e.msg.sender, spender);

    assert allowance_after == allowance_before + addedValue, "Allowance must be correctly updated";
    assert gallowances[e.msg.sender][spender] == allowance_after, "Allowance must be set correctly";
}

rule decreaseAllowance {
    env e;
    address spender;
    uint256 subtractedValue;

    mathint allowance_before = allowance(e.msg.sender, spender);

    // Requirements
    // Cannot subtract more than the allowance
    require(subtractedValue <= allowance_before);

    decreaseAllowance(e, spender, subtractedValue);

    mathint allowance_after = allowance(e.msg.sender, spender);

    assert allowance_after == allowance_before - subtractedValue, "Allowance must be correctly updated";
    assert gallowances[e.msg.sender][spender] == allowance_after, "Allowance must be set correctly";
}