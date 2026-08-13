from qbt_bridge.providers.azure import AzureQuantumProvider

# Configure the workspace via `qbt configure`, Azure CLI / DefaultAzureCredential,
# or Microsoft Entra service-principal environment variables.
provider = AzureQuantumProvider()
provider.connect()
print(provider.health())

# To execute a job, supply a provider-specific runner for your selected Azure target.
