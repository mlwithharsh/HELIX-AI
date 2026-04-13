# Contributing to HELIX AI

Thank you for your interest in contributing to HELIX. This project aims to build a world-class hybrid AI system, and your contributions are essential to its success.

## Contribution Flow
1. **Identify an Issue**: Browse the GitHub issues or create one to discuss a new idea or bug.
2. **Fork and Branch**: Fork the repository and create a branch for your work. Use the naming convention `feature/your-feature-name` or `bugfix/issue-number`.
3. **Setup Environment**: Follow the Quick Start guide in the README.
4. **Implementation**: adhere to the coding standards defined below.
5. **Testing**: Run all existing tests and add new tests for your changes.
6. **Submit PR**: Create a Pull Request against the `dev` branch. Provide a clear description of the change and link relevant issues.

## Branching Strategy
- **master**: Stable production-ready code. No direct commits allowed.
- **main**: Mirror of master.
- **dev**: Target branch for all integrations and features.
- **feature/* / bugfix/* / docs/* **: Individual working branches.

## Pull Request Rules
- All PRs must target the `dev` branch.
- Every PR must pass the CI/CD pipeline (when applicable).
- A minimum of one maintainer review is required for merging.
- Commits must be squashed before merging to maintain a clean history.

## Coding Standards
### Python (Backend)
- Follow PEP 8 style guidelines.
- Use type hints for all function signatures.
- Document classes and methods using Google-style docstrings.
- Maximum line length is 100 characters.

### Javascript (Frontend)
- Use functional components with React Hooks.
- Ensure all components are responsive and adhere to the design system.
- Use meaningful variable and function names.

## Beginner-Friendly Instructions
If you are new to open-source:
1. Look for issues labeled `good-first-issue` or `beginner`.
2. Do not hesitate to ask questions in the issue comments.
3. Start by improving documentation or adding unit tests to familiarize yourself with the codebase.
4. Join our community Discord for real-time support.

---
Maintainers reserve the right to reject PRs that do not align with the project vision or standards.
