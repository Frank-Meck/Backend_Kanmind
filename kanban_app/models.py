from django.db import models
from auth_app.models import User


class Board(models.Model):
    """
    Represents a Kanban board.

    A board groups tasks and users. Each board has an owner
    and can have multiple members who collaborate on tasks.
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Board Title",
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards",
    )

    members = models.ManyToManyField(
        User,
        related_name="boards",
        blank=True,
    )

    class Meta:
        """
        Meta configuration for Board model.

        Defines default ordering and human-readable names.
        """
        ordering = ["id"]
        verbose_name = "Board"
        verbose_name_plural = "Boards"

    def __str__(self):
        return self.title


class Task(models.Model):
    """
    Represents a task inside a board.

    Tasks are the main work units in the system.
    They can be assigned, reviewed, prioritized and tracked
    through different workflow statuses.
    """

    STATUS_TODO = "to-do"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_REVIEW = "review"
    STATUS_DONE = "done"

    STATUS_CHOICES = [
        (STATUS_TODO, "To Do"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_REVIEW, "Review"),
        (STATUS_DONE, "Done"),
    ]

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        blank=True,
        null=True,
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reviewed_tasks",
        blank=True,
        null=True,
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Task Title",
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TODO,
        verbose_name="Task Status",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name="Task Priority",
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Task Due Date",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        """
        Meta configuration for Task model.

        Defines ordering and display metadata.
        """
        ordering = ["id"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a task.

    Comments are used for discussion and collaboration
    between users on a specific task.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    content = models.TextField(
        verbose_name="Comment Content",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    class Meta:
        """
        Meta configuration for Comment model.

        Comments are ordered chronologically.
        """
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment #{self.pk}"
