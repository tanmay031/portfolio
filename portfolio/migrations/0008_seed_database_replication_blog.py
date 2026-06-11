from datetime import datetime

from django.db import migrations
from django.utils import timezone


POST_SLUG = 'database-replication-explained-scaling-reads-without-sacrificing-reliability'


POST_BODY = """As applications grow, databases often become the first bottleneck. A single database server handling every read and write request works well in the beginning, but as traffic increases, performance starts to degrade.

One of the most common solutions used by companies like Netflix, Amazon, Uber, and Spotify is **database replication**.

## The Problem with a Single Database

In a traditional architecture, every operation goes to the same database:

```mermaid
flowchart TD
    Users[Users] --> App[Application]
    App --> Db[(Single Database)]
```

That includes:

* User registrations
* Order creation
* Profile updates
* Search queries
* Dashboard reports

As traffic grows:

* Read queries increase dramatically
* Database CPU and memory usage rise
* Response times become slower
* The database becomes a single point of failure

If the database crashes, the entire application may become unavailable.

## What Is Database Replication?

Database replication is the process of maintaining multiple copies of the same database on different servers.

Typically, one database acts as the **Primary** and the others act as **Replicas**.

```mermaid
flowchart TD
    Primary[(Primary Database<br/>Writes)]
    Primary --> Replica1[(Replica 1<br/>Read Only)]
    Primary --> Replica2[(Replica 2<br/>Read Only)]
```

### How It Works

1. All write operations go to the Primary database.
2. The Primary database records the changes.
3. Changes are copied to Replica databases.
4. Read requests are distributed across replicas.

## Read and Write Separation

A common production architecture separates reads and writes.

```mermaid
flowchart LR
    User[User] --> App[Application]
    App -->|Writes| Primary[(Primary Database)]
    App -->|Reads| Replica[(Replica Database)]
```

### Write Flow

Examples:

* Creating a loan application
* Updating customer information
* Accepting an offer
* Completing a payment

These operations go to the Primary database.

### Read Flow

Examples:

* Viewing dashboards
* Fetching application history
* Reporting and analytics
* Search pages

These operations can go to Replica databases, reducing load on the Primary.

## Benefits of Database Replication

### 1. Better Read Scalability

Instead of a single database serving all read traffic, reads can be distributed across multiple replicas.

```mermaid
flowchart TD
    Reads[1000 Read Requests]
    Reads --> Rep1[(Replica 1)]
    Reads --> Rep2[(Replica 2)]
    Reads --> Rep3[(Replica 3)]
```

Result:

* Higher throughput
* Faster response times
* Better user experience

### 2. High Availability

If the Primary database fails, a replica can be promoted to become the new Primary.

```mermaid
flowchart LR
    Failed[Primary unavailable] --> Promote[Promote Replica 1]
    Promote --> NewPrimary[(New Primary)]
    Replica2[(Replica 2)] --> NewPrimary
```

This minimizes downtime and keeps the application running.

### 3. Lower Latency

Large applications often serve users globally.

```mermaid
flowchart LR
    Stockholm[Stockholm Users] --> EU[(EU Replica)]
    Tokyo[Tokyo Users] --> Asia[(Asia Replica)]
    NewYork[New York Users] --> US[(US Replica)]
```

By placing replicas closer to users, response times improve significantly.

### 4. Reporting and Analytics

Complex reporting queries can be expensive. Instead of running them on the Primary, analytics workloads can run on a replica.

```mermaid
flowchart LR
    Primary[(Primary)] --> Operations[Business Operations]
    Replica[(Replica)] --> Analytics[Analytics and Reporting]
```

This prevents reporting workloads from affecting production traffic.

## Types of Replication

### Synchronous Replication

In synchronous replication, a write is considered successful only after replicas confirm receiving the data.

```mermaid
sequenceDiagram
    participant User
    participant Primary
    participant Replica
    User->>Primary: Write request
    Primary->>Replica: Replicate change
    Replica-->>Primary: Confirm
    Primary-->>User: Success
```

Advantages:

* Strong consistency
* No data loss

Disadvantages:

* Higher write latency
* Slower performance

Best suited for:

* Financial systems
* Banking applications
* Critical transaction systems

### Asynchronous Replication

In asynchronous replication, the Primary responds immediately after writing locally. Replicas receive updates afterward.

```mermaid
sequenceDiagram
    participant User
    participant Primary
    participant Replica
    User->>Primary: Write request
    Primary-->>User: Success
    Primary->>Replica: Replicate later
```

Advantages:

* Faster writes
* Lower latency
* Better scalability

Disadvantages:

* Temporary inconsistency
* Potential data loss during failures

Best suited for:

* Social media
* Content platforms
* High-volume applications

## The Replication Lag Problem

One challenge with replication is **replication lag**.

```mermaid
flowchart TD
    Update[User updates profile] --> PrimaryUpdated[Primary updated]
    PrimaryUpdated --> Lag[Replica still catching up]
    Lag --> StaleRead[User may see outdated data]
```

The user may immediately read from a replica and see outdated data. This is called **eventual consistency**.

Common solutions:

* Read-after-write routing
* Sticky sessions
* Critical reads from Primary
* Faster replication mechanisms

## Failover: What Happens When the Primary Fails?

A modern replication setup supports automatic failover.

```mermaid
flowchart TD
    Normal[Normal state] --> Primary[(Primary)]
    Primary --> Replica1[(Replica 1)]
    Primary --> Replica2[(Replica 2)]
    Primary --> Failure[Primary fails]
    Failure --> Promotion[Replica 1 is promoted]
    Promotion --> Reconnect[Application reconnects]
    Reconnect --> Resume[Traffic resumes]
```

Tools such as PostgreSQL Patroni, Amazon RDS Multi-AZ, and Kubernetes operators automate this process.

## PostgreSQL Example

Many production systems use PostgreSQL streaming replication.

### Primary Configuration

```conf
wal_level = replica
max_wal_senders = 10
hot_standby = on
```

### Replica Behavior

* Receives WAL, or Write-Ahead Log, entries
* Replays changes locally
* Remains synchronized with Primary

This enables near real-time replication.

## How Database Replication Fits into Modern Architecture

A typical production architecture looks like this:

```mermaid
flowchart TD
    Users[Users] --> LB[Load Balancer]
    LB --> Pods[Application Pods]
    Pods -->|Writes| Primary[(Primary<br/>Writes)]
    Pods -->|Reads| Replicas[(Read Replicas<br/>Reads)]
```

This architecture is common in:

* Kubernetes deployments
* AWS RDS
* Aurora PostgreSQL
* Large-scale SaaS platforms

## Key Takeaways

Database replication is one of the most important techniques for building scalable systems.

It provides:

* Better read scalability
* High availability
* Lower latency
* Reporting isolation
* Disaster recovery capabilities

However, replication introduces trade-offs such as replication lag and consistency challenges. Understanding these trade-offs is essential when designing distributed systems.

For most modern applications, replication is the first step toward building a highly available, scalable database architecture capable of handling millions of users.
"""


def seed_database_replication_blog(apps, schema_editor):
    BlogCategory = apps.get_model('portfolio', 'BlogCategory')
    BlogPost = apps.get_model('portfolio', 'BlogPost')
    Tag = apps.get_model('portfolio', 'Tag')

    category, _ = BlogCategory.objects.get_or_create(
        slug='system-design',
        defaults={'name': 'System Design'},
    )

    post, _ = BlogPost.objects.update_or_create(
        slug=POST_SLUG,
        defaults={
            'title': 'Database Replication Explained: Scaling Reads Without Sacrificing Reliability',
            'category': category,
            'excerpt': 'A practical guide to primary databases, read replicas, replication lag, failover, and the trade-offs behind scalable database architectures.',
            'body': POST_BODY,
            'status': 'published',
            'published_at': timezone.make_aware(datetime(2026, 6, 10, 9, 0)),
            'seo_title': 'Database Replication Explained',
            'meta_description': 'Learn how database replication scales reads, improves availability, reduces latency, and what trade-offs to watch for in production systems.',
        },
    )

    tags = []
    for name, slug in (
        ('Databases', 'databases'),
        ('Scalability', 'scalability'),
        ('Backend Engineering', 'backend-engineering'),
        ('PostgreSQL', 'postgresql'),
    ):
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
        tags.append(tag)
    post.tags.set(tags)


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0007_make_excerpt_optional'),
    ]

    operations = [
        migrations.RunPython(seed_database_replication_blog, migrations.RunPython.noop),
    ]
