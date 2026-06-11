from datetime import datetime

from django.db import migrations
from django.utils import timezone


POST_SLUG = 'rabbitmq-timeout-that-wasnt-a-bug'


POST_BODY = """A few months ago, we started seeing an unusual error in production:

```text
PRECONDITION_FAILED - delivery acknowledgement timeout
```

At first, it looked like a worker had crashed.

But after checking the system, everything appeared healthy:

* Celery workers were running
* RabbitMQ was healthy
* No infrastructure issues were reported

Yet tasks were being requeued and executed again.

Something did not add up.

## Investigating the Problem

RabbitMQ expects a worker to acknowledge a message after it has finished processing it.

```mermaid
sequenceDiagram
    participant RabbitMQ
    participant Worker
    RabbitMQ->>Worker: Deliver task
    Worker->>Worker: Process task
    Worker->>RabbitMQ: ACK
```

If RabbitMQ does not receive an acknowledgement within the configured `consumer_timeout`, it assumes the consumer is no longer responding.

The channel is closed and the message can be requeued.

In our environment, the timeout was configured as:

```text
consumer_timeout = 1,800,000 ms
```

That is roughly 30 minutes.

Initially, we suspected that some long-running background jobs were taking too much time to complete. But after reviewing task execution times, we could not find evidence to support that theory.

The workers were healthy.

The tasks were completing.

Yet the timeout errors continued.

## Finding the Real Cause

After digging deeper into our asynchronous workflows, we found something interesting.

Several business processes relied on delayed execution. Instead of running immediately, some tasks were intentionally scheduled to execute:

* 24 hours later
* 48 hours later
* other long-delay intervals

A simplified example looked like this:

```python
task.apply_async(countdown=60 * 60 * 24)
```

From a business perspective, this worked perfectly.

We needed certain actions to happen one or two days later, and Celery's `countdown` feature made that easy.

However, from RabbitMQ's perspective, these delayed tasks created a different problem.

With Celery `eta` and `countdown`, workers can fetch the task before it is due. The task then waits on the worker side until its scheduled time arrives, and it is not acknowledged until execution starts.

```mermaid
sequenceDiagram
    participant RabbitMQ
    participant Worker
    RabbitMQ->>Worker: Deliver delayed task
    Worker->>Worker: Hold until countdown expires
    RabbitMQ-->>Worker: consumer_timeout exceeded
    RabbitMQ->>RabbitMQ: Close channel and requeue message
```

Eventually, RabbitMQ reached the configured timeout threshold and assumed the consumer was no longer responding.

That is why we were seeing:

```text
PRECONDITION_FAILED - delivery acknowledgement timeout
```

The issue was not a crashed worker.

The issue was not RabbitMQ being unhealthy.

The issue was how we were scheduling delayed work.

## The Immediate Fix

To stop the production issues, we increased the RabbitMQ timeout:

```text
consumer_timeout = 24 hours
```

This immediately reduced the failures and stabilized the system.

The errors disappeared, and the delayed workflows continued working.

But we knew this was not the ideal solution.

Increasing the timeout was treating the symptom, not the root cause.

## The Permanent Fix

The real issue was that RabbitMQ was being used as a scheduler.

RabbitMQ is excellent at delivering messages.

It is not the right place to hold long-delay business schedules.

So we changed the architecture.

Instead of placing long-delayed tasks directly into RabbitMQ with `countdown`, we moved those workflows to Celery Beat backed by database state.

The new flow became:

```mermaid
flowchart LR
    A[Schedule stored in Database] --> B[Celery Beat]
    B --> C[Publish task when due]
    C --> D[RabbitMQ]
    D --> E[Celery Worker]
```

Now the schedule is stored in the database.

Celery Beat continuously checks for tasks that are due.

Only when the scheduled time arrives does Beat publish the task to RabbitMQ.

As a result:

* RabbitMQ only receives work that is ready to execute
* no worker needs to wait 24 or 48 hours before acknowledging a task
* no delivery acknowledgement timeout is triggered by long countdowns
* delayed workflows become easier to monitor and manage

## The Responsibility Split

The final architecture worked because each component went back to doing the job it was designed for.

```mermaid
flowchart TD
    Schedule[Long-delay schedule] --> Database[(Database)]
    Database --> Beat[Celery Beat decides when work is due]
    Beat --> Broker[RabbitMQ delivers ready messages]
    Broker --> Worker[Celery workers execute tasks]
```

RabbitMQ delivers messages.

Celery workers execute tasks.

Celery Beat schedules tasks.

Once those responsibilities were separated, the problem disappeared.

## What We Learned

This incident was a good reminder that distributed systems often fail because of design assumptions rather than software bugs.

The error message suggested a worker problem.

The investigation initially pointed toward long-running tasks.

But the real issue was a scheduling pattern that slowly became problematic as the system evolved.

Our first fix was operational:

```text
Increase consumer_timeout
```

Our permanent fix was architectural:

```text
Move long-delayed workflows to Celery Beat
```

Sometimes the best solution is not increasing a timeout.

It is making sure each component is responsible for the job it was designed to do.
"""


def seed_rabbitmq_timeout_blog(apps, schema_editor):
    BlogCategory = apps.get_model('portfolio', 'BlogCategory')
    BlogPost = apps.get_model('portfolio', 'BlogPost')
    Tag = apps.get_model('portfolio', 'Tag')

    category, _ = BlogCategory.objects.get_or_create(
        slug='backend-engineering',
        defaults={'name': 'Backend Engineering'},
    )

    post, _ = BlogPost.objects.update_or_create(
        slug=POST_SLUG,
        defaults={
            'title': "The RabbitMQ Timeout That Wasn't a Bug",
            'category': category,
            'excerpt': 'A production story about RabbitMQ delivery acknowledgement timeouts, Celery countdown tasks, and why long-delay workflows belong in a scheduler.',
            'body': POST_BODY,
            'status': 'published',
            'published_at': timezone.make_aware(datetime(2026, 6, 12, 9, 0)),
            'seo_title': 'RabbitMQ Timeout That Was Not a Bug',
            'meta_description': 'A production debugging story about RabbitMQ consumer_timeout, Celery countdown tasks, acknowledgement timeouts, and moving delayed work to Celery Beat.',
        },
    )

    tags = []
    for name, slug in (
        ('Backend Engineering', 'backend-engineering'),
        ('RabbitMQ', 'rabbitmq'),
        ('Celery', 'celery'),
        ('Distributed Systems', 'distributed-systems'),
        ('Reliability', 'reliability'),
    ):
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
        tags.append(tag)
    post.tags.set(tags)


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0011_seed_saga_pattern_blog'),
    ]

    operations = [
        migrations.RunPython(seed_rabbitmq_timeout_blog, migrations.RunPython.noop),
    ]
