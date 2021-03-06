from typing import Any

import prefect
from prefect import Task


class StringFormatter(Task):
    """
    This task contains a template which is formatted with the results of any
    upstream tasks and returned.

    Variables from `prefect.context` are also available for formatting.

    Args:
        - template (str, optional): the optional _default_ template string to format at runtime;
            can also be provided as a keyword to `run`, which takes precendence over this default.
        - **kwargs (optional): additional keyword arguments to pass to the
            standard Task constructor
    """

    def __init__(self, template: str = None, **kwargs: Any):
        self.template = template or ""
        super().__init__(**kwargs)

    def run(self, template: str = None, **format_kwargs: Any) -> str:
        """
        Formats the template with the provided kwargs.

        Args:
            - template (str, optional): the template string to format; if not
                provided, `self.template` will be used
            - **format_kwargs (optional): keyword arguments to use for formatting

        Returns:
            - str: the formatted string
        """
        if template is None:
            template = self.template
        with prefect.context(**format_kwargs) as data:
            return template.format(**data)
