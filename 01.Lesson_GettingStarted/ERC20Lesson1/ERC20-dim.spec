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

    mathint balance_before = balanceOf(receiver);
    mathint total_supply_before = totalSupply();

    // Minting is only allowed for the owner
    // But the prover doesn't seem to care about this
    mint(e, receiver, amount);

    mathint balance_after = balanceOf(receiver);
    mathint total_supply_after = totalSupply();

    assert balance_after == balance_before + amount;
    assert total_supply_after == total_supply_before + amount;

    assert (amount > 0 && e.msg.sender == owner) => total_supply_after > 0, "minting failed";
}


// From https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/certora/specs/ERC20.spec
/*
ghost sumOfBalances() returns uint256 {
  init_state axiom sumOfBalances() == 0;
}

hook Sstore _balances[KEY address addr] uint256 newValue (uint256 oldValue) STORAGE {
    havoc sumOfBalances assuming sumOfBalances@new() == sumOfBalances@old() + newValue - oldValue;
}

invariant totalSupplyIsSumOfBalances()
    totalSupply() == sumOfBalances()
*/

rule noChangeTotalSupply(env e) {
    //requireInvariant totalSupplyIsSumOfBalances();

    method f;
    calldataarg args;

    uint256 totalSupplyBefore = totalSupply();
    f(e, args);
    uint256 totalSupplyAfter = totalSupply();

    assert totalSupplyAfter > totalSupplyBefore => f.selector == mint(address,uint256).selector;
    assert totalSupplyAfter < totalSupplyBefore => f.selector == burn(address,uint256).selector;
    assert totalSupplyAfter > totalSupplyBefore => f.selector == deposit().selector;
    assert totalSupplyAfter < totalSupplyBefore => f.selector == withdraw(uint256).selector;
}


rule transfer {
    env e;
    address recipient;
    uint256 amount;

    mathint sender_balance_before = balanceOf(e.msg.sender);
    mathint recipient_balance_before = balanceOf(recipient);
    mathint total_supply_before = totalSupply();

    transfer(e, recipient, amount);

    mathint sender_balance_after = balanceOf(e.msg.sender);
    mathint recipient_balance_after = balanceOf(recipient);
    mathint total_supply_after = totalSupply();

    assert sender_balance_after == sender_balance_before - amount;
    assert recipient_balance_after == recipient_balance_before + amount;
    assert total_supply_after == total_supply_before;
}
