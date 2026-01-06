# AWS S3 (Simple Storage Service)

## What is S3?

S3 (Simple Storage Service) is **one of the main building blocks of AWS**. It's advertised as "infinitely scaling" storage and serves as the backbone for many websites and AWS services as an integration point.

S3 is object storage that allows you to store and retrieve any amount of data from anywhere on the web. Unlike traditional file systems or block storage, S3 is object-based storage where each file is stored as an independent object with its own metadata.

**Key Characteristics:**
- Infinitely scalable storage
- 99.999999999% durability (11 nines) across multiple AZs
- Highly available (varies by storage class)
- Object-based storage (not file or block based)
- Accessed via web interface, CLI, or APIs
- Pay only for what you use
- Industry standard for cloud storage

**Real-World Examples:**
- **Nasdaq**: Stores 7 years of data in S3 Glacier
- **Sysco**: Analyzes data and obtains commercial insights using S3

**Common Use Cases:**
- Backup and storage
- Disaster recovery
- Archive and compliance data
- Hybrid cloud storage
- Application hosting
- Media hosting (images, videos)
- Data lakes for big data analytics
- Software delivery
- Static website hosting

## S3 Core Concepts

### Buckets

Buckets are containers (directories) for objects stored in S3.

**Bucket Characteristics:**
- Must have **globally unique name across all AWS accounts and all regions**
- Defined at **region level** (despite global namespace)
- S3 looks like a global service, but buckets are created in a region
- Naming convention:
  - No uppercase letters, no underscores
  - 3-63 characters long
  - Not an IP address format
  - Must start with lowercase letter or number
  - Must NOT start with prefix `xn--`
  - Must NOT end with suffix `-s3alias`

**Bucket Naming Best Practices:**
- Use DNS-compliant names
- Include project or application identifier
- Include environment if applicable (dev, staging, prod)
- Example: `myapp-prod-static-assets-us-east-1`

### Objects

Objects (files) are stored in buckets and have a key.

**Object Key Structure:**
- The key is the **FULL path** to the object
- Key = prefix + object name
- Examples:
  - `s3://my-bucket/my-file.txt` → key: `my-file.txt`
  - `s3://my-bucket/my-folder1/another-folder/my-file.txt` → key: `my-folder1/another-folder/my-file.txt`
- Key composed of: **prefix** + **object name**
  - `s3://my-bucket/my_folder1/another_folder/my-file.txt`
  - Prefix: `my_folder1/another_folder/`
  - Object name: `my-file.txt`

**Important**: There's no concept of "directories" within buckets (although the UI will make you think otherwise). Everything is a key with slashes in the name.

**Object Components:**
- **Key**: The full path to the object (including "folders")
- **Value**: The actual content/data (body of the object)
  - Max object size: 5TB (5000GB)
  - If uploading more than 5GB, must use "multi-part upload"
- **Metadata**: List of text key-value pairs (system or user metadata)
- **Tags**: Key-value pairs (up to 10) - useful for security/lifecycle
- **Version ID**: If versioning enabled, unique identifier for object version

### Object Size Limitations

**Single PUT Operation:**
- Maximum 5GB per PUT operation

**Multi-Part Upload:**
- **Required** for objects larger than 5GB
- **Recommended** for objects over 100MB
- Maximum object size: 5TB
- Uploads object in parts (minimum 5MB per part, except last part)
- Benefits:
  - Improved throughput (parallel uploads)
  - Quick recovery from network issues
  - Pause and resume uploads
  - Begin upload before knowing final object size

## S3 Security

S3 provides multiple layers of security that can be combined for defense in depth.

### User-Based Security

**IAM Policies:**
- Attached to IAM users, groups, or roles
- Define which API calls are allowed for specific users from IAM
- Example: Allow user to read from specific bucket
- Best for: Controlling AWS user/application access

### Resource-Based Security

**Bucket Policies:**
- JSON-based policies attached to buckets
- **Most common** way to configure S3 security
- Rules from S3 console - allows cross-account access
- Can grant cross-account access
- Can make bucket public
- More flexible than ACLs
- Example use cases:
  - Grant public read access to static website
  - Allow specific AWS account to access bucket
  - Force objects to be encrypted at upload
  - Grant access to another account (cross-account)

**Bucket Policy Structure (JSON):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::examplebucket/*"]
    }
  ]
}
```

Components:
- **Resource**: Buckets and objects
- **Effect**: Allow or Deny
- **Action**: Set of API to Allow or Deny
- **Principal**: The account or user to apply the policy to

**Object Access Control Lists (ACLs):**
- Finer-grained control (can be disabled)
- Legacy method (less common now)
- AWS recommends using bucket policies instead

**Bucket Access Control Lists (ACLs):**
- Less common (can be disabled)
- Legacy method
- AWS recommends using bucket policies instead

### IAM Permissions Evaluation Logic

**Critical for Exam**: An IAM principal can access an S3 object if:
- The user IAM permissions **ALLOW** it **OR** the resource policy **ALLOWS** it
- **AND** there's no explicit **DENY**

### Encryption

**Encrypt objects in S3 using encryption keys**

S3 supports encryption both at rest and in transit.

**Encryption at Rest:**

1. **Server-Side Encryption (SSE)**
   
   - **SSE-S3**: AWS manages encryption keys
     - Encryption using keys handled, managed, and owned by AWS
     - AES-256 encryption
     - Enabled by default for new buckets and objects
     - Header: `x-amz-server-side-encryption: AES256`
   
   - **SSE-KMS**: AWS Key Management Service
     - Encryption using keys handled and managed by AWS KMS
     - More control over keys
     - Audit trail of key usage in CloudTrail
     - Header: `x-amz-server-side-encryption: aws:kms`
     - Additional costs for KMS API calls
   
   - **SSE-C**: Customer-Provided Keys
     - You manage encryption keys outside of AWS
     - AWS performs encryption/decryption but doesn't store the key
     - Keys must be provided with each request
     - **HTTPS must be used**
     - Not available via AWS Console (only SDK/CLI)

2. **Client-Side Encryption**
   - Encrypt data before sending to S3
   - You manage encryption process and keys entirely
   - Use client libraries (AWS Encryption SDK)
   - Decrypt data client-side when retrieving

**Encryption in Transit:**
- Use HTTPS endpoints (SSL/TLS)
- S3 exposes both HTTP and HTTPS endpoints
- HTTPS recommended and **required for SSE-C**
- Can enforce HTTPS-only via bucket policy

**Encryption Best Practices:**
- Enable default encryption on all buckets
- Use SSE-KMS for sensitive data requiring audit trails
- Enforce encryption via bucket policy
- Use HTTPS for all data transfers

### Block Public Access Settings

**These settings were created to prevent company data leaks**

S3 provides four settings to prevent accidental public exposure of data. If you know your bucket should never be public, leave these settings enabled.

**Block Public Access Settings (4 options):**
1. **Block public access to buckets and objects granted through NEW access control lists (ACLs)**
2. **Block public access to buckets and objects granted through ANY access control lists (ACLs)**
3. **Block public access to buckets and objects granted through NEW public bucket or access point policies**
4. **Block public and cross-account access to buckets and objects through ANY public bucket or access point policies**

**Important Notes:**
- Can be set at **account level** or **bucket level**
- Account-level settings override bucket-level
- Enabled by default for new buckets and accounts
- Even if bucket policy allows public access, Block Public Access settings override it
- Leave these ON unless you have specific reason to allow public access (e.g., static website hosting)

## S3 Static Website Hosting

S3 can host static websites and have them accessible on the internet.

**Website URL Format (depending on region):**
- `http://<bucket-name>.s3-website-<aws-region>.amazonaws.com`
- `http://<bucket-name>.s3-website.<aws-region>.amazonaws.com`

**Configuration:**
- Enable static website hosting on bucket
- Specify index document (e.g., `index.html`)
- Optionally specify error document (e.g., `error.html`)
- Make bucket publicly readable (bucket policy or ACL)

**Important**: If you get a **403 Forbidden** error, make sure the bucket policy allows public reads!

**Requirements:**
- Bucket name must match domain name (if using custom domain)
- Objects must be publicly readable
- All files uploaded to bucket

**Use Cases:**
- Static portfolio or blog sites
- Single Page Applications (SPAs)
- Documentation sites
- Temporary event sites
- Landing pages

**Best Practices:**
- Use CloudFront for:
  - HTTPS support
  - Better performance (caching)
  - Custom domain with SSL certificate
  - DDoS protection
- Use Route 53 for custom domain DNS
- Enable versioning for easy rollbacks
- Use lifecycle policies to manage costs

## S3 Versioning

You can version your files in Amazon S3.

**How Versioning Works:**
- Enabled at **bucket level**
- Same key overwrite will change the "version": 1, 2, 3...
- Each object gets unique Version ID
- Protects against unintended deletes and overwrites
- Can restore to previous versions
- **Best practice**: Version your buckets

**Version ID Behavior:**
- New objects: Get unique version ID
- Updates: Create new version with new version ID
- Deletes: Add "delete marker" (can be removed to restore)
- **Any file that is not versioned prior to enabling versioning will have version "null"**
- **Suspending versioning does not delete previous versions**

**Benefits:**
- Protection against unintended deletes (ability to restore a version)
- Easy rollback to previous versions
- Archive old versions for compliance

**Considerations:**
- Storage costs: You pay for all versions
- Deleting: Need to delete all versions to truly remove object
- Lifecycle policies can help manage old versions

**Notes:**
- Once enabled, versioning can only be suspended (not disabled)
- Files uploaded before versioning have Version ID "null"

## S3 Replication

Replication automatically copies objects between buckets.

**Prerequisites:**
- **Must enable Versioning** in source and destination buckets
- Buckets can be in different AWS accounts
- Must give S3 proper IAM permissions
- Copying is asynchronous

**Types of Replication:**

**Cross-Region Replication (CRR):**
- Replicates objects to bucket in different region
- Use cases:
  - Compliance requirements
  - Lower latency access for global users
  - Replication across accounts
  - Disaster recovery

**Same-Region Replication (SRR):**
- Replicates objects to bucket in same region
- Use cases:
  - Log aggregation
  - Live replication between production and test accounts
  - Compliance (separate copy with different encryption)

**Replication Behavior:**

- **After enabling Replication, only new objects are replicated**
- Optionally, you can replicate existing objects using **S3 Batch Replication**
  - Replicates existing objects and objects that failed replication

**For delete operations:**
- **Can replicate delete markers** from source to target (optional setting)
- Deletions with a version ID are **not replicated** (to avoid malicious deletes)

**Important Note - No "chaining" of replication:**
- If bucket 1 has replication into bucket 2, which has replication into bucket 3
- Then objects created in bucket 1 are **not replicated** to bucket 3

**Replication Features:**
- Can replicate to multiple destinations
- Can change storage class during replication
- Can change ownership of replicas

## S3 Storage Classes

S3 offers different storage classes optimized for different use cases and access patterns.

**Overview:**
- Amazon S3 Standard - General Purpose
- Amazon S3 Standard-Infrequent Access (IA)
- Amazon S3 One Zone-Infrequent Access (IA)
- Amazon S3 Glacier Instant Retrieval
- Amazon S3 Glacier Flexible Retrieval
- Amazon S3 Glacier Deep Archive
- Amazon S3 Intelligent-Tiering

**Can move between classes manually or using S3 Lifecycle configurations**

### Durability and Availability

**Durability:**
- **High durability (99.999999999%, 11 9's)** of objects across multiple AZ
- If you store 10,000,000 objects with Amazon S3, you can on average expect to incur a loss of a single object once every 10,000 years
- **Same for all storage classes**

**Availability:**
- Measures how readily available a service is
- Varies depending on storage class
- Example: S3 Standard has 99.99% availability = not available 53 minutes a year

### Standard Storage Classes

**S3 Standard - General Purpose:**
- 99.99% availability
- Used for frequently accessed data
- Low latency and high throughput
- Sustain 2 concurrent facility failures
- Use cases: Big Data analytics, mobile & gaming applications, content distribution

**S3 Intelligent-Tiering:**
- Small monthly monitoring and auto-tiering fee
- Moves objects automatically between access tiers based on usage
- There are no retrieval charges in S3 Intelligent-Tiering
- Tiers:
  - **Frequent Access tier** (automatic): default tier
  - **Infrequent Access tier** (automatic): objects not accessed for 30 days
  - **Archive Instant Access tier** (automatic): objects not accessed for 90 days
  - **Archive Access tier** (optional): configurable from 90 to 700+ days
  - **Deep Archive Access tier** (optional): configurable from 180 to 700+ days
- Use cases: Unknown or changing access patterns

### Infrequent Access Classes

**S3 Standard-IA (Infrequent Access):**
- For data that is less frequently accessed, but requires rapid access when needed
- Lower cost than S3 Standard
- 99.9% availability
- Use cases: Disaster recovery, backups

**S3 One Zone-IA:**
- High durability (99.999999999%) in a single AZ; data lost when AZ is destroyed
- 99.5% availability
- Lower cost than Standard-IA (~20% cost savings)
- Use cases: Storing secondary backup copies of on-premises data, or data you can recreate

### Archive Classes

**S3 Glacier Instant Retrieval:**
- Low-cost object storage meant for archiving/backup
- Millisecond retrieval, great for data accessed once a quarter
- Minimum storage duration of 90 days
- Use cases: Data accessed once per quarter, medical images, news media assets

**S3 Glacier Flexible Retrieval (formerly Amazon S3 Glacier):**
- Retrieval options:
  - **Expedited**: 1 to 5 minutes
  - **Standard**: 3 to 5 hours
  - **Bulk**: 5 to 12 hours (free)
- Minimum storage duration of 90 days
- Use cases: Long-term backups, disaster recovery archives

**S3 Glacier Deep Archive:**
- **Lowest cost** storage class
- For long-term storage
- Retrieval options:
  - **Standard**: 12 hours
  - **Bulk**: 48 hours
- Minimum storage duration of 180 days
- Use cases: Long-term retention for regulatory compliance (7-10 years)

### Storage Class Comparison Table

| Feature | Standard | Intelligent-Tiering | Standard-IA | One Zone-IA | Glacier Instant | Glacier Flexible | Glacier Deep |
|---------|----------|-------------------|-------------|-------------|-----------------|------------------|--------------|
| **Durability** | 99.999999999% (11 9's) across all classes |
| **Availability** | 99.99% | 99.9% | 99.9% | 99.5% | 99.9% | 99.99% | 99.99% |
| **Availability SLA** | 99.9% | 99% | 99% | 99% | 99% | 99.9% | 99.9% |
| **Availability Zones** | ≥3 | ≥3 | ≥3 | 1 | ≥3 | ≥3 | ≥3 |
| **Min Storage Duration** | None | None | 30 days | 30 days | 90 days | 90 days | 180 days |
| **Min Billable Object Size** | None | None | 128 KB | 128 KB | 128 KB | 40 KB | 40 KB |
| **Retrieval Fee** | None | None | Per GB | Per GB | Per GB | Per GB | Per GB |

### Storage Class Pricing (Example: us-east-1)

| Storage Class | Storage Cost (per GB/month) | Retrieval Cost (per 1000 requests) | Retrieval Time |
|--------------|---------------------------|----------------------------------|----------------|
| **Standard** | $0.023 | GET: $0.0004, POST: $0.005 | Instant |
| **Intelligent-Tiering** | $0.0025 - $0.023 | GET: $0.0004, POST: $0.005 | Instant |
| **Standard-IA** | $0.0125 | GET: $0.001, POST: $0.01 | Instant |
| **One Zone-IA** | $0.01 | GET: $0.001, POST: $0.01 | Instant |
| **Glacier Instant** | $0.004 | GET: $0.01, POST: $0.02 | Instant |
| **Glacier Flexible** | $0.0036 | Expedited: $10, Standard: $0.05, Bulk: Free | Expedited: 1-5 min, Standard: 3-5 hrs, Bulk: 5-12 hrs |
| **Glacier Deep** | $0.00099 | Standard: $0.10, Bulk: $0.025 | Standard: 12 hrs, Bulk: 48 hrs |

**Additional Costs:**
- **Intelligent-Tiering**: Monitoring cost of $0.0025 per 1000 objects

**Reference**: https://aws.amazon.com/s3/pricing/

**Storage Class Selection Criteria:**
- Access frequency
- Retrieval time requirements
- Durability vs availability needs
- Cost optimization goals
- Compliance requirements

## S3 Lifecycle Policies

Lifecycle policies automatically transition or expire objects based on rules you define.

**Transition Actions:**
- Move objects between storage classes
- Example: Move to Standard-IA after 30 days, Glacier after 90 days
- Can define multiple transitions
- Rules based on object age (creation date)

**Expiration Actions:**
- Delete objects after specified time
- Delete old versions (if versioning enabled)
- Delete incomplete multipart uploads
- Example: Delete objects older than 365 days

**Lifecycle Rule Components:**
- Rule scope: Apply to entire bucket, prefix, or tags
- Transition rules: When and where to move objects
- Expiration rules: When to delete objects
- Status: Enabled or Disabled

**Common Lifecycle Patterns:**

1. **Log Management:**
   - Keep logs in Standard for 30 days
   - Move to Standard-IA for 60 days
   - Move to Glacier for 1 year
   - Delete after 7 years

2. **Backup Optimization:**
   - Recent backups in Standard-IA
   - Monthly backups to Glacier Flexible
   - Annual backups to Glacier Deep Archive
   - Delete backups older than 10 years

3. **Multipart Upload Cleanup:**
   - Delete incomplete multipart uploads after 7 days
   - Saves storage costs from failed uploads

**Best Practices:**
- Start with current versions, then apply to non-current versions
- Test rules on subset before applying to entire bucket
- Use S3 Storage Class Analysis to identify access patterns
- Combine with S3 Intelligent-Tiering for unknown patterns

## S3 Performance Optimization

### Request Performance

**Baseline Performance:**
- **3,500 PUT/COPY/POST/DELETE requests per second per prefix**
- **5,500 GET/HEAD requests per second per prefix**
- No limit on number of prefixes in bucket

**Prefix Definition:**
- Everything between bucket name and object name
- Example: `bucket/folder1/folder2/file.txt`
  - Prefix: `folder1/folder2/`
- **Distribute objects across prefixes for better performance**
- If you spread reads across all four prefixes evenly, you can achieve 22,000 requests per second for GET and HEAD

**Performance Optimization Strategies:**

1. **Multi-Part Upload:**
   - Parallelize uploads
   - **Recommended** for files > 100MB
   - **Required** for files > 5GB
   - Can improve upload speed significantly

2. **S3 Transfer Acceleration:**
   - Uses CloudFront edge locations
   - Upload to edge location, then transfer to S3 over AWS private network
   - Can achieve 50-500% faster uploads
   - Compatible with multipart upload
   - Additional cost per GB transferred
   - Use AWS Transfer Acceleration Speed Comparison tool

3. **S3 Byte-Range Fetches:**
   - Parallelize downloads by requesting byte ranges
   - Better resilience (retry only failed range, not entire file)
   - Can download only specific parts of file
   - Example: Get only first 10 bytes to read file header
   - Can be used to speed up downloads (parallelize GETs)

### Caching with CloudFront

- Reduce load on S3 by caching at edge locations
- Improve read performance globally
- Reduce S3 request costs
- TTL controls how long objects cached

## S3 Event Notifications

S3 can trigger events when certain actions occur.

**Event Types:**
- Object created (PUT, POST, COPY, CompleteMultipartUpload)
- Object removed (DELETE)
- Object restore from Glacier
- Replication events
- Lifecycle events

**Event Destinations:**
- **SNS Topics**: Send notifications to subscribers
- **SQS Queues**: Queue for processing by applications
- **Lambda Functions**: Execute serverless code
- **EventBridge**: Route to multiple destinations, advanced filtering

**Use Cases:**
- Generate thumbnails when images uploaded
- Process data files automatically
- Trigger workflows based on file arrival
- Audit and compliance logging
- Data validation pipelines

**EventBridge Advantages:**
- Advanced filtering with JSON rules
- Multiple destinations per rule
- Archive and replay events
- No need to configure resource policies
- Integration with 18+ AWS services

## S3 Access Logs

S3 can log all requests made to buckets for audit purposes.

**Server Access Logging:**
- Logs all requests to bucket
- Delivered to another S3 bucket (logging bucket)
- Log format: Apache-like
- Best effort delivery (not guaranteed)
- May take hours for logs to appear

**Log Information Includes:**
- Requester account and IP address
- Bucket and object key
- Request time and HTTP status
- Error code if applicable
- Bytes sent
- Request type (GET, PUT, DELETE, etc.)

**Important Considerations:**
- **Never set logging bucket same as monitored bucket** (logging loop)
- Logging bucket should have different ownership or strict access control
- Use lifecycle policies to manage log retention and costs

**Alternative: CloudTrail Data Events:**
- More detailed than access logs
- Near real-time
- Integration with CloudWatch Logs
- Higher cost than S3 access logs
- Use for compliance and detailed audit trails

## S3 CORS (Cross-Origin Resource Sharing)

CORS allows web applications in one domain to access resources in another domain.

**When CORS Needed:**
- Web browser makes request to different origin
- Origin = protocol + domain + port
- Example: `https://example.com` accessing `https://bucket.s3.amazonaws.com`

**CORS Configuration:**
- JSON or XML document attached to bucket
- Specifies:
  - Allowed origins
  - Allowed methods (GET, PUT, POST, DELETE)
  - Allowed headers
  - Exposed headers
  - Max age (cache duration)

**Common Use Case:**
- Static website in one S3 bucket
- Assets (images, scripts) in another bucket
- Browser requires CORS to load cross-origin assets

**Example CORS Policy:**
```json
[
    {
        "AllowedOrigins": ["https://example.com"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedHeaders": ["*"],
        "MaxAgeSeconds": 3000
    }
]
```

## S3 Consistency Model

**Current Consistency:**
- **Strong read-after-write consistency** for all operations
- Applies to all S3 regions
- No eventual consistency delays

**What This Means:**
- PUT new object → immediately visible in GET
- Update existing object → immediately see new version
- DELETE object → immediately returns 404
- List objects → immediately reflects changes
- No additional cost for strong consistency

**Previous Behavior (before Dec 2020):**
- Eventual consistency for overwrites and deletes
- Modern S3 no longer has this limitation

## Important S3 Limits

**Bucket Limits:**
- 100 buckets per account (soft limit - can request increase)
- Bucket names globally unique
- No limit on objects per bucket
- No limit on total storage

**Object Limits:**
- Minimum object size: 0 bytes
- Maximum object size: 5 TB
- Maximum single PUT: 5 GB
- Multipart upload required for > 5 GB

**Request Limits:**
- 3,500 PUT/COPY/POST/DELETE per second per prefix
- 5,500 GET/HEAD per second per prefix

**Metadata Limits:**
- System metadata: AWS-managed
- User metadata: Max 2 KB
- Object tags: Max 10 tags per object

## Cost Optimization Strategies

1. **Choose Right Storage Class:**
   - Analyze access patterns
   - Use S3 Storage Class Analysis
   - Implement lifecycle policies

2. **Use Lifecycle Policies:**
   - Automatically transition to cheaper classes
   - Delete old data
   - Clean up incomplete multipart uploads

3. **Enable S3 Intelligent-Tiering:**
   - For unpredictable access patterns
   - Automatic cost optimization

4. **Optimize Data Transfer:**
   - Use CloudFront to reduce S3 requests
   - Compress files before uploading
   - Use S3 Transfer Acceleration only when needed

5. **Monitor and Analyze:**
   - Use S3 Storage Lens for visibility
   - Review CloudWatch metrics
   - Analyze access patterns with S3 Storage Class Analysis

6. **Request Optimization:**
   - Use byte-range fetches for large files
   - Implement client-side caching
   - Batch operations when possible

## Common Exam Scenarios

**Scenario: Host static website**
- Solution: S3 static website hosting + CloudFront + Route 53
- Enable public read access (disable Block Public Access)
- Configure index/error documents
- If 403 Forbidden: Check bucket policy allows public reads

**Scenario: Reduce latency globally**
- Solution: CloudFront in front of S3
- Or: S3 Transfer Acceleration for uploads

**Scenario: Secure sensitive data**
- Solution: SSE-KMS encryption + bucket policy enforce HTTPS + Block Public Access enabled

**Scenario: Automatically delete old data**
- Solution: S3 Lifecycle policy with expiration rule

**Scenario: Disaster recovery cross-region**
- Solution: Cross-Region Replication (CRR) + versioning enabled

**Scenario: Unknown access patterns**
- Solution: S3 Intelligent-Tiering

**Scenario: Long-term archive (7+ years)**
- Solution: S3 Glacier Deep Archive

**Scenario: Process files as uploaded**
- Solution: S3 Event Notifications → Lambda

**Scenario: High-performance uploads**
- Solution: Multipart upload + multiple prefixes + S3 Transfer Acceleration

**Scenario: Compliance audit trail**
- Solution: CloudTrail data events + S3 access logs

**Scenario: Protect against accidental deletes**
- Solution: Enable versioning + MFA Delete

**Scenario: Replicate only new objects**
- Solution: Enable replication after objects created
- For existing: Use S3 Batch Replication

**Scenario: Cost optimization for varying access patterns**
- Solution: S3 Intelligent-Tiering (no retrieval fees)