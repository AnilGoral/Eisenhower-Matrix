from dataclasses import dataclass, field
from typing import Any, Optional, List
from enum import Enum


class ActionType(Enum):
    ADD_TASK = "add_task"
    DELETE_TASK = "delete_task"
    EDIT_TASK = "edit_task"
    MOVE_TASK = "move_task"
    STATUS_CHANGE = "status_change"
    DUE_DATE_CHANGE = "due_date_change"
    NOTES_CHANGE = "notes_change"


@dataclass
class Action:
    action_type: ActionType
    task_id: str
    data: dict = field(default_factory=dict)
    description: str = ""


class UndoManager:
    """Manages undo/redo stack for task operations."""

    MAX_STACK_SIZE = 20

    def __init__(self):
        self._undo_stack: List[Action] = []
        self._redo_stack: List[Action] = []

    def record(self, action: Action):
        """Record an action for undo."""
        self._undo_stack.append(action)
        if len(self._undo_stack) > self.MAX_STACK_SIZE:
            self._undo_stack.pop(0)
        # Clear redo stack on new action
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self) -> Optional[Action]:
        """Pop and return the last action to undo."""
        if self._undo_stack:
            action = self._undo_stack.pop()
            self._redo_stack.append(action)
            return action
        return None

    def redo(self) -> Optional[Action]:
        """Pop and return the last action to redo."""
        if self._redo_stack:
            action = self._redo_stack.pop()
            self._undo_stack.append(action)
            return action
        return None

    def last_action_description(self) -> str:
        if self._undo_stack:
            return self._undo_stack[-1].description
        return ""
