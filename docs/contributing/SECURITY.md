# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in r⁵py, please report it privately to
the maintainers to allow for a coordinated fix.

- **GitHub Security Advisories**: [Report a
  vulnerability](https://github.com/r5py/r5py/security/advisories/new)

Please provide as much detail as possible, including steps to reproduce the
issue and any relevant logs or screenshots.

## Security Practices

We adhere to the following security measures to ensure the safety and integrity
of the r⁵py project:

### Dependency Management

- Utilise GitHub’s Dependabot to monitor and update dependencies with known
  vulnerabilities.
- Regularly audit dependencies for security issues.

### Code Quality and Review

- Enforce code formatting standards using tools like `black` and `flake8`.
- Require code reviews for all pull requests to ensure adherence to security and
  quality standards.

### Sensitive Data Handling

- Prohibit the inclusion of sensitive information (e.g., passwords, API keys) in
  the codebase.
- Implement checks to detect and prevent accidental commits of sensitive data.

### Access Control

- Apply the principle of least privilege for repository access.
- Require two-factor authentication (2FA) for all contributors with write
  access.

### Continuous Integration and Deployment

- Use GitHub Actions with restricted permissions to automate testing and
  deployment.
- Ensure that CI/CD pipelines do not expose sensitive information.

## Contributor Responsibilities

All contributors are expected to follow the [contribution
guidelines](https://r5py.readthedocs.io/en/stable/contributing/CONTRIBUTING.html)
and adhere to security best practices, including:

- Regularly updating local development environments to incorporate the latest
  security patches.
- Reviewing and testing code changes for potential security issues before
  submission.
- Promptly addressing any security concerns raised during code reviews.

## Contact

For any security-related inquiries or concerns, please contact the
[maintainers](https://github.com/r5py/r5py/security/advisories/new).

---

This security policy is intended to evolve over time. We welcome feedback and
suggestions to improve our security practices.

--- 
