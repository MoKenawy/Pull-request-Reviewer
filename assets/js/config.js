/* Frontend settings. Switch USE_MOCK_API to false only when the Python API contract is confirmed. */
window.REVIEWER_CONFIG = Object.freeze({
  USE_MOCK_API: true,
  API_BASE_URL: "http://127.0.0.1:8000",
  CODE_REVIEW_ENDPOINT: "/api/v1/reviews/code",
  PR_REVIEW_ENDPOINT: "/api/v1/reviews/github-pr",
  REQUEST_TIMEOUT_MS: 90000,
  MAX_FILE_BYTES: 1024 * 1024
});
