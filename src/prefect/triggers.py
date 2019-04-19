"""
Triggers are functions that determine if task state should change based on
the state of preceding tasks.
"""
from toolz import curry
from typing import Callable, Set, Union

from prefect import context
from prefect.engine import signals, state


def all_finished(upstream_states: Set["state.State"]) -> bool:
    """
    This task will run no matter what the upstream states are, as long as they are finished.

    Args:
        - upstream_states (set[State]): the set of all upstream states
    """
    if not all(s.is_finished() for s in upstream_states):
        raise signals.TRIGGERFAIL(
            'Trigger was "all_finished" but some of the upstream tasks were not finished.'
        )

    return True


def manual_only(upstream_states: Set["state.State"]) -> bool:
    """
    This task will never run automatically, because this trigger will
    always place the task in a Paused state. The only exception is if
    the "resume" keyword is found in the Prefect context, which happens
    automatically when a task starts in a Resume state.

    Args:
        - upstream_states (set[State]): the set of all upstream states
    """
    if context.get("resume"):
        return True

    raise signals.PAUSE('Trigger function is "manual_only"')


def all_successful(upstream_states: Set["state.State"]) -> bool:
    """
    Runs if all upstream tasks were successful. Note that `SKIPPED` tasks are considered
    successes and `TRIGGER_FAILED` tasks are considered failures.

    Args:
        - upstream_states (set[State]): the set of all upstream states
    """

    if not all(s.is_successful() for s in upstream_states):
        raise signals.TRIGGERFAIL(
            'Trigger was "all_successful" but some of the upstream tasks failed.'
        )
    return True


def all_failed(upstream_states: Set["state.State"]) -> bool:
    """
    Runs if all upstream tasks failed. Note that `SKIPPED` tasks are considered successes
    and `TRIGGER_FAILED` tasks are considered failures.

    Args:
        - upstream_states (set[State]): the set of all upstream states
    """

    if not all(s.is_failed() for s in upstream_states):
        raise signals.TRIGGERFAIL(
            'Trigger was "all_failed" but some of the upstream tasks succeeded.'
        )
    return True


def any_successful(upstream_states: Set["state.State"]) -> bool:
    """
    Runs if any tasks were successful. Note that `SKIPPED` tasks are considered successes
    and `TRIGGER_FAILED` tasks are considered failures.

    Args:
        - upstream_states (set[State]): the set of all upstream states
    """

    if not any(s.is_successful() for s in upstream_states):
        raise signals.TRIGGERFAIL(
            'Trigger was "any_successful" but none of the upstream tasks succeeded.'
        )
    return True


def any_failed(upstream_states: Set["state.State"]) -> bool:
    """
    Runs if any tasks failed. Note that `SKIPPED` tasks are considered successes and
    `TRIGGER_FAILED` tasks are considered failures.

    Args:
        - upstream_states (set[State]): the set of all upstream states
    """

    if not any(s.is_failed() for s in upstream_states):
        raise signals.TRIGGERFAIL(
            'Trigger was "any_failed" but none of the upstream tasks failed.'
        )
    return True


@curry
def some_failed(
    upstream_states: Set["state.State"],
    at_least: Union[int, float] = None,
    at_most: Union[int, float] = None,
) -> bool:
    """
    Runs if some amount of upstream tasks failed. This amount can be specified as an upper bound (`at_most`) or
    a lower bound (`at_least`), and can be provided as an absolute number or a percentage of upstream tasks.

    Note that `SKIPPED` tasks are considered successes and `TRIGGER_FAILED` tasks are considered failures.

    Args:
        - at_least (Union[int, float], optional): the minimum number of upstream failures that must occur for
            this task to run.  If the provided number is less than 0, it will be interpreted as a percentage, otherwise as an
            absolute number.
        - at_most (Union[int, float], optional): the maximum number of upstream failures to allow for
            this task to run.  If the provided number is less than 0, it will be interpreted as a percentage, otherwise as an
            absolute number.
        - upstream_states (set[State]): the set of all upstream states
    """

    # scale conversions
    num_failed = len([s for s in upstream_states if s.is_failed()])
    num_states = len(upstream_states)
    if at_least is not None:
        at_least = (num_states * at_least) if at_least < 1 else at_least
    else:
        at_least = 0
    if at_most is not None:
        at_most = (num_states * at_most) if at_most < 1 else at_most
    else:
        at_most = num_states

    if not (at_least <= num_failed <= at_most):
        raise signals.TRIGGERFAIL(
            'Trigger was "all_failed" but some of the upstream tasks succeeded.'
        )
    return True


# aliases
always_run = all_finished  # type: Callable[[Set["state.State"]], bool]
