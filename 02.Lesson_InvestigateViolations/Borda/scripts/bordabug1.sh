SOLC_VERSION="0.7.0"

solc-select install $SOLC_VERSION
solc-select use $SOLC_VERSION

certoraRun BordaBug1.sol:Borda \
  --verify Borda:specs/BordaBug1Dim.spec \
#  --msg "$1"