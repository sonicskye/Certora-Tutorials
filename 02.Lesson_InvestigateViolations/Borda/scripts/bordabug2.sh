SOLC_VERSION="0.7.0"

solc-select install $SOLC_VERSION
solc-select use $SOLC_VERSION

certoraRun BordaBug2.sol:Borda \
  --verify Borda:specs/BordaBug2Dim.spec \
#  --msg "$1"