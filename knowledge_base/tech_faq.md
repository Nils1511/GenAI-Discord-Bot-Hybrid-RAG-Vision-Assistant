# Tech FAQ

## How do I reset my password?
Go to the company portal at portal.company.com/reset. Enter your employee email address and click "Reset Password." You'll receive an email within 5 minutes with a reset link. The link expires after 24 hours.

## What VPN should I use?
We use WireGuard VPN for all remote connections. Download the config file from the IT portal under "VPN Access." Import it into the WireGuard client. Contact IT support if you need a new config file generated.

## How do I set up my development environment?
1. Clone the monorepo: `git clone git@github.com:company/monorepo.git`
2. Install Docker Desktop (latest stable version)
3. Run `make setup` to install dependencies and seed the database
4. Run `make dev` to start the development server on port 3000
5. See the CONTRIBUTING.md file for coding standards

## What CI/CD pipeline do we use?
We use GitHub Actions for CI/CD. Every pull request triggers:
- Linting (ESLint + Prettier)
- Unit tests (Jest)
- Integration tests (Playwright)
- Security scanning (Snyk)
- Build verification

Deployments to staging happen automatically on merge to `develop`. Production deployments require a manual approval gate.

## How do I request new software?
Submit a ticket on the IT Service Desk at helpdesk.company.com. Include:
- Software name and version
- Business justification
- Whether it requires a license purchase
- Urgency level

Standard requests are processed within 3 business days.

## How do I access the database?
Production database access is restricted. For read-only access:
1. Request access via the IT portal
2. Get manager approval
3. Use the provided read-replica connection string
4. Never run write queries against production

For development, use the local Docker database spun up by `make dev`.
