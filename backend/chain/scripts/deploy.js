const hre = require("hardhat");

async function main() {
  console.log("==================================================");
  console.log("Deploying Verification.sol to Polygon Amoy...");
  console.log("==================================================");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deployer Address:", deployer.address);

  const Verification = await hre.ethers.getContractFactory("Verification");
  const verification = await Verification.deploy();

  await verification.waitForDeployment();
  const address = await verification.getAddress();

  console.log("✅ Verification.sol deployed successfully!");
  console.log("Contract Address:", address);
  console.log("\nUpdate your .env file with:");
  console.log(`CONTRACT_ADDRESS=${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
