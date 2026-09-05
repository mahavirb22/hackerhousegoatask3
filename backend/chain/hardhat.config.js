require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../../.env" });

const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000";
const POLYGON_AMOY_URL = process.env.WEB3_PROVIDER_URL || "https://rpc-amoy.polygon.technology";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    polygonAmoy: {
      url: POLYGON_AMOY_URL,
      accounts: [PRIVATE_KEY],
      chainId: 80002,
    },
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};
