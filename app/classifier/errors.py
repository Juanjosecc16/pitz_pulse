"""Exception hierarchy for the classification pipeline.

Retryable errors are transient (timeouts, provider overload, malformed output)
and the service tries again. Provider errors (bad credentials, bad request)
will not fix themselves, so they fail fast.
"""


class ClassifierError(Exception):
    """Base class for every classification error."""


class LLMProviderError(ClassifierError):
    """Non-retryable provider failure (authentication, invalid request, etc.)."""


class RetryableLLMError(ClassifierError):
    """Transient failure: the same request may succeed on a new attempt."""


class LLMTimeoutError(RetryableLLMError):
    """The model did not answer within the configured timeout."""


class LLMUnavailableError(RetryableLLMError):
    """Network error, rate limit or provider-side (5xx) error."""


class InvalidLLMResponseError(RetryableLLMError):
    """The model answered, but the output is not a valid classification."""


class ClassificationFailedError(ClassifierError):
    """Raised by the service when a request could not be classified."""
