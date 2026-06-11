from datetime import datetime

from django.db import migrations
from django.utils import timezone


POST_SLUG = 'saga-pattern-keeping-distributed-systems-consistent'


POST_BODY = """Imagine a customer places an order on an e-commerce platform.

Behind the scenes, a single click triggers multiple services:

* Order Service creates the order
* Payment Service reserves the money
* Inventory Service reserves the product
* Shipping Service prepares delivery
* Notification Service sends confirmation

At first glance, this looks like a single transaction. In reality, each service owns its own database and operates independently.

```mermaid
flowchart LR
    A[Customer Places Order] --> B[Order Service]
    B --> C[Payment Service]
    C --> D[Inventory Service]
    D --> E[Shipping Service]
    E --> F[Notification Service]
```

Everything works perfectly until something fails.

The payment is successfully reserved. The order exists. But when the Inventory Service checks stock, it discovers that the last item was already sold.

Now the system is in an inconsistent state:

* Order exists
* Payment is reserved
* Product is unavailable

Without a recovery mechanism, the customer could be charged for something that cannot be delivered.

This is where the **Saga Pattern** becomes useful.

Instead of relying on one large database transaction, the workflow is broken into a sequence of smaller local transactions. When a step fails, the system performs compensating actions to bring the workflow back to a valid state.

```mermaid
flowchart TD
    A[Create Order] --> B[Reserve Payment]
    B --> C[Reserve Inventory]
    C -->|Success| D[Prepare Shipment]
    D --> E[Complete Order]
    C -->|Failed| F[Release Payment]
    F --> G[Cancel Order]
```

In this scenario, the compensation is not simply deleting records. The system intentionally executes business actions:

1. Release the payment reservation
2. Mark the order as cancelled
3. Store the failure reason
4. Notify the customer

The result is a system that can recover gracefully from partial failures.

## Why This Matters

In modern distributed systems, failures are not exceptional events. They are expected events.

Network interruptions happen. Services become unavailable. External APIs return errors. The Saga Pattern embraces this reality by focusing on recovery rather than assuming every step will succeed.

```mermaid
flowchart LR
    Failure[Partial Failure] --> Detect[Detect Failed Step]
    Detect --> Compensate[Run Compensation]
    Compensate --> ValidState[Return to Valid State]
    ValidState --> Observable[Record What Happened]
```

## What I Learned

Working with distributed workflows taught me that the most important design question is not:

> How does the happy path work?

but rather:

> What happens when step 3 succeeds and step 4 fails?

The Saga Pattern provides a structured answer to that question, making complex systems more reliable, observable, and resilient.
"""


def seed_saga_pattern_blog(apps, schema_editor):
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
            'title': 'Saga Pattern: Keeping Distributed Systems Consistent',
            'category': category,
            'excerpt': 'A story-driven explanation of how the Saga Pattern helps distributed systems recover from partial failures with compensating actions.',
            'body': POST_BODY,
            'status': 'published',
            'published_at': timezone.make_aware(datetime(2026, 6, 11, 10, 0)),
            'seo_title': 'Saga Pattern in Distributed Systems',
            'meta_description': 'Learn how the Saga Pattern keeps distributed systems consistent by using local transactions and compensating actions when workflow steps fail.',
        },
    )

    tags = []
    for name, slug in (
        ('System Design', 'system-design'),
        ('Distributed Systems', 'distributed-systems'),
        ('Backend Engineering', 'backend-engineering'),
        ('Reliability', 'reliability'),
    ):
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
        tags.append(tag)
    post.tags.set(tags)


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0010_seed_privacy_first_http_log_analytics_blog'),
    ]

    operations = [
        migrations.RunPython(seed_saga_pattern_blog, migrations.RunPython.noop),
    ]
