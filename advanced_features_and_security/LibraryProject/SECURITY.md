# Security hardening notes

- Production `DEBUG` off via `DJANGO_DEBUG`; hosts configured via `DJANGO_ALLOWED_HOSTS`.
- Cookies marked secure: `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`.
- Browser protections: `SECURE_CONTENT_TYPE_NOSNIFF=True`, `X_FRAME_OPTIONS='DENY'`, XSS header enabled, plus CSP header via `LibraryProject.middleware.CSPMiddleware` using `CONTENT_SECURITY_POLICY` setting.
- CSRF: all forms include `{% csrf_token %}`.
- Data access: `book_list` uses a validated form (`BookSearchForm`) and ORM filters to avoid SQL injection.
- CSP default: `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self';` (override `CONTENT_SECURITY_POLICY` as needed per deployment).

Basic test checklist:
- Verify HTTP responses include `Content-Security-Policy`, `X-Frame-Options`, and `X-Content-Type-Options` headers.
- Ensure cookies are marked `Secure` when served over HTTPS.
- Exercise forms (search, example) and confirm CSRF tokens are present; submitting without token should fail.
- Attempt XSS payloads in search field; output should be escaped by templates and restricted by CSP.
