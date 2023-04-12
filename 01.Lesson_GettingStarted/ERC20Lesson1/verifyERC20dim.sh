SOLC_VERSION="0.8.0"

solc-select install $SOLC_VERSION
solc-select use $SOLC_VERSION

certoraRun ERC20.sol:ERC20 --verify ERC20:ERC20-dim.spec \
  --msg "$1"