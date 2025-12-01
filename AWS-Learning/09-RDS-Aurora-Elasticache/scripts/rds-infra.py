import boto3
import logging
import dotenv
import os
import time
from typing import Dict, Optional, Any
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RDSInfra:
    """
    Manages AWS RDS infra operations
    
    - Database instance creation with proper security groups
    - Instance state management (start, stop, delete)
    - Configuration retrieval and monitoring
    
    Attributes:
        client: boto3
        region: AWS availability zone
    """
    
    def __init__(self, region_name: str = 'mx-central-1'):
        """
        Initialize RDS infrastructure manager.
        Args:
            region_name (str, optional): _description_. Defaults to 'mx-central-1'.
        """
        self.client = boto3.client('rds', region_name=region_name)
        self.region = region_name
        logger.info(f"RDS Infrastructure Manager initialized for region: {region_name}")
        
    def create_database_instance(
        self,
        db_instance_identifier: str,
        db_name: str,
        master_username: str,
        master_password: str,
        db_instance_class: str = 'db.t3.micro',
        allocated_storage: int = 20,
        engine: str = 'postgres',
        engine_version: str = '17.6',
        publicly_accessible: bool = True,
        backup_retention_period: int = 7,
        storage_encrypted: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new RDS PostgreSQL instance.
        
        This method provisions a new RDS instance with the following considerations:
        - Free tier eligible configuration (db.t3.micro, 20GB)
        - Automatic backups enabled (7-day retention)
        - Storage encryption enabled for security
        - Public accessibility for learning/development (disable in production)

        Args:
            db_instance_identifier (str): _description_
            db_name (str): _description_
            master_username (str): _description_
            master_password (str): _description_
            db_instance_class (str, optional): _description_. Defaults to 'db.t3.micro'.
            allocated_storage (int, optional): _description_. Defaults to 20.
            engine (str, optional): _description_. Defaults to 'postgres'.
            engine_version (str, optional): _description_. Defaults to '17.6'.
            publicly_accessible (bool, optional): _description_. Defaults to True.
            backup_retention_period (int, optional): _description_. Defaults to 7.
            storage_encrypted (bool, optional): _description_. Defaults to True.

        Returns:
            Dict containing RDS instance creation response
            
        Raises:
            ClientError: If RDS instance creation fails
        """
        try:
            logger.info(f"Creating RDS instance: {db_instance_identifier}")
            
            if engine_version is None:
                logger.info("No engine version specified, getting latest available...")
                versions_response = self.client.describe_db_engine_versions(
                    Engine=engine,
                    DefaultOnly=True
                )
                if versions_response['DBEngineVersions']:
                    engine_version = versions_response['DBEngineVersions'][0]['EngineVersion']
                    logger.info(f"Using default engine version: {engine_version}")
                else:
                    # Fallback:
                    engine_version = '16.1'
                    logger.info(f"Using fallback engine version: {engine_version}")
            
            response = self.client.create_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                DBName=db_name,
                MasterUsername=master_username,
                MasterUserPassword=master_password,
                DBInstanceClass=db_instance_class,
                Engine=engine,
                EngineVersion=engine_version,
                AllocatedStorage=allocated_storage,
                StorageType='gp3',  # Latest generation general purpose SSD
                StorageEncrypted=storage_encrypted,
                PubliclyAccessible=publicly_accessible,
                BackupRetentionPeriod=backup_retention_period,
                # Enable automated minor version patches
                AutoMinorVersionUpgrade=True,
                # Enable Performance Insights (useful for monitoring)
                EnablePerformanceInsights=False,  # Keep false for free tier
                # Multi-AZ deployment (set False for free tier)
                MultiAZ=False,
                # Deletion protection (recommended for production)
                DeletionProtection=False,
                # Tags for resource organization
                Tags=[
                    {'Key': 'Environment', 'Value': 'Development'},
                    {'Key': 'ManagedBy', 'Value': 'boto3'},
                    {'Key': 'Purpose', 'Value': 'AWS-Learning'}
                ]
            )
            
            logger.info(f"RDS instance creation initiated successfully")
            logger.info(f"Instance ID: {db_instance_identifier}")
            logger.info(f"Status: {response['DBInstance'].get('DBInstanceStatus', 'Unknown')}")
            
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to create RDS instance: {error_code} - {error_message}")
            raise
        
    def wait_for_instance_available(
        self,
        db_instance_identifier: str,
        max_attempts: int = 60,
        delay: int = 30
    ) -> bool:
        logger.info(f"Waiting for instance {db_instance_identifier} to become available...")
        
        try:
            waiter = self.client.get_waiter('db_instance_available')
            waiter.wait(
                DBInstanceIdentifier=db_instance_identifier,
                WaiterConfig={
                    'Delay': delay,
                    'MaxAttempts': max_attempts
                }
            )
            logger.info(f"Instance {db_instance_identifier} is now available!")
            return True
            
        except Exception as e:
            logger.error(f"Error waiting for instance: {str(e)}")
            return False
        
    def get_instance_details(self, db_instance_identifier: str) -> Optional[Dict]:
        try:
            response = self.client.describe_db_instances(
                DBInstanceIdentifier=db_instance_identifier
            )
            
            if not response['DBInstances']:
                logger.warning(f"Instance {db_instance_identifier} not found")
                return None
            
            instance = response['DBInstances'][0]
            
            # Extract key connection information
            details = {
                'identifier': instance['DBInstanceIdentifier'],
                'status': instance['DBInstanceStatus'],
                'engine': f"{instance['Engine']} {instance['EngineVersion']}",
                'instance_class': instance['DBInstanceClass'],
                'storage': f"{instance['AllocatedStorage']}GB",
                'endpoint': instance.get('Endpoint', {}).get('Address', 'Not available yet'),
                'port': instance.get('Endpoint', {}).get('Port', 'Not available yet'),
                'availability_zone': instance.get('AvailabilityZone', 'Unknown'),
                'publicly_accessible': instance['PubliclyAccessible'],
                'backup_retention': instance['BackupRetentionPeriod'],
                'created_time': instance.get('InstanceCreateTime', 'Unknown')
            }
            
            logger.info(f"Retrieved details for instance: {db_instance_identifier}")
            return details
            
        except ClientError as e:
            logger.error(f"Error retrieving instance details: {e.response['Error']['Message']}")
            return None
        
    def get_connection_string(self, db_instance_identifier: str) -> Optional[str]:
        details = self.get_instance_details(db_instance_identifier)
        
        if not details or details['endpoint'] == 'Not available yet':
            logger.warning("Instance endpoint not available yet")
            return None
        
        # Note: Username and password need to be provided separately
        connection_string = (
            f"postgresql://{{username}}:{{password}}@"
            f"{details['endpoint']}:{details['port']}/{{dbname}}"
        )
        
        logger.info("Connection string template generated")
        return connection_string
    
    def stop_instance(self, db_instance_identifier: str) -> Dict:
        try:
            logger.info(f"Stopping RDS instance: {db_instance_identifier}")
            response = self.client.stop_db_instance(
                DBInstanceIdentifier=db_instance_identifier
            )
            logger.info(f"Instance stop initiated: {db_instance_identifier}")
            return response
            
        except ClientError as e:
            logger.error(f"Error stopping instance: {e.response['Error']['Message']}")
            raise
        
    def start_instance(self, db_instance_identifier: str) -> Dict:
        try:
            logger.info(f"Starting RDS instance: {db_instance_identifier}")
            response = self.client.start_db_instance(
                DBInstanceIdentifier=db_instance_identifier
            )
            logger.info(f"Instance start initiated: {db_instance_identifier}")
            return response
            
        except ClientError as e:
            logger.error(f"Error starting instance: {e.response['Error']['Message']}")
            raise
        
    def delete_instance(
        self,
        db_instance_identifier: str,
        skip_final_snapshot: bool = True,
        final_snapshot_identifier: Optional[str] = None
    ) -> Dict:
        try:
            logger.warning(f"Deleting RDS instance: {db_instance_identifier}")
            
            params = {
                'DBInstanceIdentifier': db_instance_identifier,
                'SkipFinalSnapshot': skip_final_snapshot
            }
            
            if not skip_final_snapshot and final_snapshot_identifier:
                params['FinalDBSnapshotIdentifier'] = final_snapshot_identifier
            
            response = self.client.delete_db_instance(**params)
            logger.warning(f"Instance deletion initiated: {db_instance_identifier}")
            return response
            
        except ClientError as e:
            logger.error(f"Error deleting instance: {e.response['Error']['Message']}")
            raise
        
    def list_all_instances(self) -> list:
        try:
            response = self.client.describe_db_instances()
            instances = [
                {
                    'identifier': db['DBInstanceIdentifier'],
                    'status': db['DBInstanceStatus'],
                    'engine': f"{db['Engine']} {db['EngineVersion']}",
                    'endpoint': db.get('Endpoint', {}).get('Address', 'Not available')
                }
                for db in response['DBInstances']
            ]
            
            logger.info(f"Found {len(instances)} RDS instances")
            return instances
            
        except ClientError as e:
            logger.error(f"Error listing instances: {e.response['Error']['Message']}")
            return []

def main():
    rds = RDSInfra(region_name='mx-central-1')
    
    
    dotenv.load_dotenv()
    
    DB_INSTANCE_ID = 'pgdb-learning'
    DB_NAME = 'mydb'
    MASTER_USERNAME = 'postgres'
    MASTER_PASSWORD = os.getenv('MYPASS')
    
    # Step 1: Create RDS instance
    print("\n=== Creating RDS Instance ===")
    try:
        create_response = rds.create_database_instance(
            db_instance_identifier=DB_INSTANCE_ID,
            db_name=DB_NAME,
            master_username=MASTER_USERNAME,
            master_password=MASTER_PASSWORD
        )
        print(f"✓ Instance creation initiated: {DB_INSTANCE_ID}")
        
    except ClientError as e:
        print(f"✗ Failed to create instance: {e.response['Error']['Message']}")
        return
    
    # Step 2: Wait for instance to be available
    print("\n=== Waiting for Instance to be Available ===")
    print("This typically takes 5-10 minutes...")
    
    is_available = rds.wait_for_instance_available(DB_INSTANCE_ID)
    
    if not is_available:
        print("✗ Instance did not become available in time")
        return
    
    # Step 3: Get connection details
    print("\n=== Instance Connection Details ===")
    details = rds.get_instance_details(DB_INSTANCE_ID)
    
    if details:
        print(f"Endpoint: {details['endpoint']}")
        print(f"Port: {details['port']}")
        print(f"Status: {details['status']}")
        print(f"Engine: {details['engine']}")
        
        connection_string = rds.get_connection_string(DB_INSTANCE_ID)
        print(f"\nConnection String Template:")
        print(connection_string)
        print(f"\nFull Connection String:")
        print(connection_string.format(
            username=MASTER_USERNAME,
            password='YOUR_PASSWORD',
            dbname=DB_NAME
        ))
    
    # Step 4: List all instances
    print("\n=== All RDS Instances ===")
    instances = rds.list_all_instances()
    for idx, instance in enumerate(instances, 1):
        print(f"{idx}. {instance['identifier']} - {instance['status']} - {instance['engine']}")
        
if __name__ == "__main__":
    main()