# RDS, Aurora and Elasticache

---

## Content

- [RDS, Aurora and Elasticache](#rds-aurora-and-elasticache)
  - [Content](#content)
    - [Introduction](#introduction)
    - [List of important ports you should know](#list-of-important-ports-you-should-know)
  - [Practice](#practice)
    - [How to create an RDS SQL Database](#how-to-create-an-rds-sql-database)
    - [How to create an ElastiCache Redis Database](#how-to-create-an-elasticache-redis-database)

---

### Introduction

### List of important ports you should know

Importan ports:

- FTP:    `21`
- SSH:    `22`
- SFTP:   `22`
- HTTP:   `80`
- HTTPS:  `443`

RDS DB Points:

- PostgreSQL: `5432`
- MySQL: `3306`
- Oracle RDS: `1521`
- MSSQL Server: `1433`
- MariaDB: `3306`
- Aurora (PostgreSQL): `5432`
- Aurora (MySQL): `3306`

---

## Practice

### How to create an RDS SQL Database

1. Navigate to the AWS Console
![alt text](./images/01-aws-console.png)

2. Search for RDS at the search bar
![alt text](./images/02-search.png)

3. Click on "Create a database"
![alt text](./images/03-create-a-database.png)
4. Select our desired DB
![alt text](./images/04-select-db.png)
5. Select the DB template
![alt text](./images/05-db-template.png)
6. Type the name of your DB
![alt](./images/06-db-name.png)
7. Select "Self managed" as our "Credentials management" and type a secure password
![alt](./images/07-credentials.png)
8. Select instance configuration as the most basic one (free tier)
![x](./images/08-instance.png)
9. For storage select the basic one, and set 20 GiB as a storage volume (20 is the minumum)
![Storage Config](./images/09-storage-config.png)
10. Adjusting connectivity
![conn](./images/10-conn.png)
11. Creating new security group
![sg](./images/11-create-sg.png)
And remember your port number
![port](./images/11-1-port.png)
12. Set DB Auth as is (we already created a password for this)
![auth](./images/12-auth-pass.png)
13. Set the initial DB name and enable the automated backup
![name](./images/13-name.png)
14. Configure monitoring (we are unchecking it)
![disable-monitoring](./images/14-monitoring.png)
15. And we are done
![done](./images/15-done.png)

### How to create an ElastiCache Redis Database

![WARNING]
RDS Storage Auto Scale