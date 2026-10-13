import os
from locust import HttpUser, task, between, events

SERVICE_URL = os.environ.get("SERVICE_URL", "").strip()
P95_MS_THRESHOLD = float(os.environ.get("PERF_P95_MS_THRESHOLD", "500"))
FAIL_RATIO_THRESHOLD = float(os.environ.get("PERF_FAIL_RATIO_THRESHOLD", "0.01"))

class GeneratedUser(HttpUser):
    host = SERVICE_URL
    wait_time = between(0.5, 1.5)

    @task
    def get_root(self):
        """A simple task to hit the root URL of the service."""
        self.client.get("/")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    This listener is triggered when the test run stops.
    It checks the final stats against the defined thresholds and
    sets the exit code to 1 (failure) if they are not met.
    """
    stats = environment.stats.total
    fail_ratio = stats.fail_ratio
    p95_ms = stats.get_response_time_percentile(0.95)

    if fail_ratio > FAIL_RATIO_THRESHOLD:
        print(f"Test failed: Failure ratio ({fail_ratio:.4f}) exceeded threshold ({FAIL_RATIO_THRESHOLD})")
        environment.process_exit_code = 1

    if p95_ms and p95_ms >= P95_MS_THRESHOLD:
        print(f"Test failed: P95 response time ({p95_ms:.2f} ms) exceeded threshold ({P95_MS_THRESHOLD} ms)")
        environment.process_exit_code = 1

    if environment.process_exit_code == 0:
        print("Performance thresholds met successfully.")
