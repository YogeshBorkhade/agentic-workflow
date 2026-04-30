"""
Error handling and retry logic with Tenacity.
Prevents runaway costs and handles transient LLM failures.
"""

import asyncio
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec
from datetime import datetime, timedelta

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)

from src.config import settings
from src.utils import logger


# Type hints for decorators
P = ParamSpec('P')
T = TypeVar('T')


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM call times out."""
    pass


class LLMInvalidResponseError(LLMError):
    """Raised when LLM returns invalid/unparseable response."""
    pass


class TokenBudgetExceededError(Exception):
    """Raised when token budget is exceeded."""
    pass


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open (too many failures)."""
    pass


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    States:
    - CLOSED: Normal operation, requests go through
    - OPEN: Too many failures, reject all requests
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            # Check if recovery timeout has passed
            if (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout:
                logger.info(f"Circuit breaker {self.name}: Entering HALF_OPEN state")
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker {self.name} is OPEN. "
                    f"Too many failures. Try again later."
                )
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset or close circuit
            if self.state == "HALF_OPEN":
                logger.info(f"Circuit breaker {self.name}: Closing (service recovered)")
                self.state = "CLOSED"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit breaker {self.name}: Opening "
                    f"({self.failure_count} failures)"
                )
                self.state = "OPEN"
            
            raise


class TokenBudget:
    """
    Track token usage to prevent runaway costs.
    
    Enforces daily/hourly limits on token consumption.
    """
    
    def __init__(
        self,
        daily_limit: int = 100_000,
        hourly_limit: int = 10_000,
        name: str = "default"
    ):
        self.daily_limit = daily_limit
        self.hourly_limit = hourly_limit
        self.name = name
        
        self.daily_usage = 0
        self.hourly_usage = 0
        self.day_start = datetime.now().date()
        self.hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    def _reset_if_needed(self) -> None:
        """Reset counters if day/hour has changed."""
        now = datetime.now()
        current_day = now.date()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        if current_day > self.day_start:
            logger.info(f"Token budget {self.name}: Daily reset ({self.daily_usage} tokens used)")
            self.daily_usage = 0
            self.day_start = current_day
        
        if current_hour > self.hour_start:
            logger.info(f"Token budget {self.name}: Hourly reset ({self.hourly_usage} tokens used)")
            self.hourly_usage = 0
            self.hour_start = current_hour
    
    def check_and_consume(self, tokens: int) -> None:
        """
        Check if tokens are available and consume them.
        
        Args:
            tokens: Number of tokens to consume
            
        Raises:
            TokenBudgetExceededError: If budget exceeded
        """
        self._reset_if_needed()
        
        # Check limits
        if self.daily_usage + tokens > self.daily_limit:
            raise TokenBudgetExceededError(
                f"Daily token limit exceeded for {self.name}. "
                f"Used: {self.daily_usage}, Limit: {self.daily_limit}"
            )
        
        if self.hourly_usage + tokens > self.hourly_limit:
            raise TokenBudgetExceededError(
                f"Hourly token limit exceeded for {self.name}. "
                f"Used: {self.hourly_usage}, Limit: {self.hourly_limit}"
            )
        
        # Consume tokens
        self.daily_usage += tokens
        self.hourly_usage += tokens
        
        logger.debug(
            f"Token budget {self.name}: Consumed {tokens} tokens. "
            f"Daily: {self.daily_usage}/{self.daily_limit}, "
            f"Hourly: {self.hourly_usage}/{self.hourly_limit}"
        )
    
    def get_usage(self) -> dict:
        """Get current usage statistics."""
        self._reset_if_needed()
        return {
            "daily_usage": self.daily_usage,
            "daily_limit": self.daily_limit,
            "daily_remaining": self.daily_limit - self.daily_usage,
            "hourly_usage": self.hourly_usage,
            "hourly_limit": self.hourly_limit,
            "hourly_remaining": self.hourly_limit - self.hourly_usage,
        }


def retry_with_backoff(
    max_attempts: int | None = None,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts (default from settings)
        exceptions: Tuple of exceptions to retry on
        
    Example:
        @retry_with_backoff(max_attempts=3)
        def call_llm():
            ...
    """
    if max_attempts is None:
        max_attempts = settings.max_retries
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, "WARNING"),
        after=after_log(logger, "INFO"),
        reraise=True,
    )


def timeout(seconds: float | None = None) -> Callable:
    """
    Decorator to add timeout to async functions.
    
    Args:
        seconds: Timeout in seconds (default from settings)
        
    Example:
        @timeout(30.0)
        async def call_llm():
            ...
    """
    if seconds is None:
        seconds = settings.timeout_seconds
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise LLMTimeoutError(
                    f"{func.__name__} timed out after {seconds} seconds"
                )
        return wrapper
    return decorator


# Global instances (singleton pattern)
_circuit_breakers = {}
_token_budgets = {}


def get_circuit_breaker(name: str = "default") -> CircuitBreaker:
    """Get or create circuit breaker by name."""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name=name)
    return _circuit_breakers[name]


def get_token_budget(name: str = "default") -> TokenBudget:
    """Get or create token budget by name."""
    if name not in _token_budgets:
        _token_budgets[name] = TokenBudget(name=name)
    return _token_budgets[name]


# Example usage
if __name__ == "__main__":
    import time
    
    print("Testing error handling framework...\n")
    
    # Test 1: Retry with backoff
    print("1. Testing retry with exponential backoff:")
    
    @retry_with_backoff(max_attempts=3, exceptions=(ValueError,))
    def flaky_function(attempt: list):
        attempt[0] += 1
        print(f"   Attempt {attempt[0]}")
        if attempt[0] < 3:
            raise ValueError("Transient error")
        return "Success!"
    
    attempt_counter = [0]
    result = flaky_function(attempt_counter)
    print(f"   Result: {result}\n")
    
    # Test 2: Circuit breaker
    print("2. Testing circuit breaker:")
    breaker = get_circuit_breaker("test")
    
    def failing_service():
        raise Exception("Service unavailable")
    
    for i in range(7):
        try:
            breaker.call(failing_service)
        except (Exception, CircuitBreakerOpen) as e:
            print(f"   Attempt {i+1}: {type(e).__name__}")
    print()
    
    # Test 3: Token budget
    print("3. Testing token budget:")
    budget = get_token_budget("test")
    budget.daily_limit = 100
    budget.hourly_limit = 50
    
    try:
        budget.check_and_consume(30)
        print(f"   Consumed 30 tokens: {budget.get_usage()}")
        
        budget.check_and_consume(25)
        print(f"   Consumed 25 tokens: {budget.get_usage()}")
        
        budget.check_and_consume(10)  # This should fail (hourly limit)
    except TokenBudgetExceededError as e:
        print(f"   ❌ {e}")
    
    print("\n✅ Error handling framework configured successfully!")