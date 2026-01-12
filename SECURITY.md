# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Janus-1 seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: 112788717+ChessEngineUS@users.noreply.github.com

Include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

After you submit a report, we will:

1. **Acknowledge receipt** within 48 hours
2. **Provide an initial assessment** of the report within 5 business days
3. **Work with you** to understand and validate the issue
4. **Develop and test a fix** as quickly as possible
5. **Release the fix** and publicly disclose the vulnerability details
6. **Credit you** in the security advisory (if desired)

### Safe Harbor

We support safe harbor for security researchers who:

- Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our services
- Only interact with accounts you own or with explicit permission of the account holder
- Do not exploit a security issue for any reason (This includes demonstrating additional risk, such as attempted compromise of sensitive company data or probing for additional issues)
- Do not violate any other applicable laws or regulations

### Security Updates

Security updates will be released through:

- GitHub Security Advisories
- CHANGELOG.md entries marked with `[SECURITY]`
- Release notes on GitHub Releases

### Best Practices for Users

To keep your Janus-1 installation secure:

1. **Keep updated**: Always use the latest version
2. **Review dependencies**: Regularly update Python dependencies with `pip install --upgrade -r requirements.txt`
3. **Use virtual environments**: Isolate Janus-1 and its dependencies
4. **Monitor advisories**: Watch this repository for security updates
5. **Validate inputs**: When using Janus-1 in production, validate all user inputs
6. **Secure your quantum hardware access**: If connecting to real quantum devices, use proper authentication

### Security Considerations for Quantum Computing

Janus-1 operates in the quantum computing domain. Be aware that:

- Quantum circuits may contain sensitive information about algorithms or research
- Circuit optimization strategies could be considered intellectual property
- When connecting to cloud quantum providers, ensure proper credential management
- Results from quantum simulations should be validated before use in critical applications

### Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release new versions with the fix
5. Prominently announce the problem in release notes

We aim for a 90-day disclosure timeline from initial report to public disclosure, though this may be adjusted based on:

- Severity and exploitability of the vulnerability
- Complexity of the required fix
- Coordination with affected third parties
- Active exploitation in the wild

### Comments on This Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue.

### Recognition

We maintain a list of security researchers who have responsibly disclosed vulnerabilities to us. If you'd like to be listed, please let us know when you submit your report.

## Thank You

Thank you for helping keep Janus-1 and our users safe!