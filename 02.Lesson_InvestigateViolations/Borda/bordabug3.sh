SOLC_VERSION="0.7.0"

solc-select install $SOLC_VERSION
solc-select use $SOLC_VERSION

certoraRun BordaBug3.sol:Borda \
  --verify Borda:BordaBug2Dim.spec \
#  --msg "$1"