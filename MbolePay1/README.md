Mbole Pay – A Distributed Digital Njangi Platform for Africa
Abstract
This document presents a comprehensive project description for Mbole Pay, a distributed digital platform designed to modernise traditional African Njangi (tontine) savings systems. The platform is intended to provide a scalable, secure and fault-tolerant environment for group savings, automated payouts, dispute resolution and collaborative management. The report covers the problem statement, problem scope, proposed solution, system architecture, technology stack, literature review, implementation plan, a detailed calendar of activities from October 2025 to February 2026, expected outcomes, and references. The design emphasizes microservices, containerization, cloud-based distribution, monitoring, and DevOps practices to ensure availability, reliability and maintainability. The project is prepared at the undergraduate level and the document aims to serve as a submission-ready report for academic evaluation.

Table of Contents
1. Introduction
2. Problem Description
3. Problem Scope
4. Literature Review
5. Proposed Solution
6. System Design and Architecture
7. Technology Stack and Tools
8. Non-Functional Requirements: Scalability, Fault Tolerance, Collaboration
9. Implementation Plan
10. Calendar of Activities (October 2025 - February 2026)
11. Expected Outcomes
12. Conclusion and Recommendations
13. References


1. Introduction
Njangi, also referred to as 'tontine', 'esusu', 'chama' or other local terms across Africa, represents a deeply embedded community savings practice in which members make regular monetary contributions that are pooled and disbursed to members on a rotating basis. These informal groups promote mutual support, liquidity management and social cohesion. Despite the cultural importance and wide adoption of Njangi systems, many groups still rely on manual record-keeping and face challenges associated with trust, transparency and scalability. Mbole Pay is conceived as a digital platform intended to preserve the social structure and cultural value of Njangi while addressing operational inefficiencies through automation, transparent record-keeping and cloud-based distribution. This report describes the rationale, design, implementation plan, and evaluation criteria for Mbole Pay.
2. Problem Description
Traditional Njangi systems operate on interpersonal trust and manual processes. A designated treasurer often maintains a physical ledger or local spreadsheet to record contributions and payouts. Such manual approaches are error-prone and vulnerable to misconduct. Common challenges include misplaced records, arithmetic errors, delays in payout distribution, and disputes that erode trust among members. Additionally, the absence of a consistent process for dispute resolution and audit trails permits fraud or mismanagement. Scalability presents another major issue: groups that begin with a small number of members often encounter operational difficulties as membership increases or when members become geographically dispersed. Technology adoption is limited by cost, digital literacy and the lack of culturally appropriate digital interfaces. Mbole Pay seeks to mitigate these challenges by offering an accessible, transparent and culturally sensitive digital platform that automates contributions, transparently logs transactions and provides tools for collaborative decision-making.
3. Problem Scope
The scope of the Mbole Pay project includes the design and development of a frontend prototype and a complete project specification for a full-stack distributed system prepared for implementation. This report assumes an initial operational scope targeted at informal Njangi groups with basic digital access such as smartphones and internet connectivity. The project scope includes user registration, group creation, contribution scheduling, contribution tracking, payout scheduling, dispute voting and basic notification services. Excluded from the initial scope are integration with specific national payment providers in production (which are listed as future work), full blockchain mainnet deployment, and extensive legal or regulatory compliance activities which require jurisdiction-specific legal review. The system is designed to be extensible to support integration with mobile money APIs, biometric authentication and regional compliance measures in future development phases.
4. Literature Review
This section summarizes relevant literature and existing solutions related to community savings, fintech interventions in Africa, and technical approaches for distributed financial applications. Research on rotating savings and credit associations (ROSCAs) and their digitization indicates both the social importance and the technical challenges of automating such systems. Studies have shown that digitization of ROSCAs can increase participation rates, reduce leakage and improve record accuracy (Aker, Boumnijel, McClellan, & Tierney, 2016). Several digital products and platforms have targeted informal savings groups. Examples include Esusu, M-Shwari, and various microfinance fintech companies that provide complementary services such as savings, lending, and automated transfers. These platforms demonstrate the viability of digital financial services in African markets but also highlight barriers such as trust, regulatory constraints, and integration with existing mobile money ecosystems.
From a technical perspective, distributed systems research provides guidance for building fault-tolerant and scalable services. Microservices architectures, container orchestration with Kubernetes, and cloud-native design patterns have been widely adopted in industry to achieve elasticity and resilience (Newman, 2015). For financial systems, additional concerns arise around data consistency, transaction integrity and latencies. Event-driven architectures and the use of immutable logs (for auditability) are common practices in fintech systems. Blockchain and smart contracts have been proposed as mechanisms for increasing transparency and automating agreements; however, concerns about transaction costs, privacy and regulatory acceptance remain relevant considerations for practical deployment (Catalini & Gans, 2016).
The literature indicates that a hybrid approach—combining traditional cloud services for scalability and optional blockchain components for critical transparency features—can balance practical constraints with the benefits of decentralization. Mbole Pay draws on these findings to propose a cloud-first, distributed microservices architecture with optional smart contract integration for selected workflows.
5. Proposed Solution
Mbole Pay is proposed as a cloud-native application that digitizes Njangi group operations while preserving their collaborative and social nature. The platform provides the following core capabilities:
User Management: Secure user registration and authentication with role-based access control to support members, group administrators, and auditors.
Group Management: Create and manage Njangi groups with configurable contribution amounts, schedules, and payout sequences.
Contribution Tracking: Record and display member contributions in real time; support scheduled contributions via seeding or integrations.
Automated Payouts: Support both rule-based automated payouts and future integration with smart contracts to ensure that payouts follow agreed rules.
Dispute Resolution: Provide a voting mechanism for members to resolve disputes, with results logged for auditability. The platform includes notification features for reminders, confirmations and alerts related to contributions and payouts.
Privacy and Security: Use encryption for data in transit and at rest, secure authentication, and audit logging to meet expected confidentiality and integrity requirements.
The design emphasizes modularity, extensibility and cultural sensitivity in the user interface to accommodate varied literacy and language needs.
6. System Design and Architecture
This section describes the recommended system architecture for Mbole Pay. The system follows a microservices architecture organized into the following logical services: authentication service, user profile service, group management service, contribution service, payout service, notification service and an audit/logging service. Each service exposes a well-defined RESTful or gRPC API and persists its data to a dedicated schema in a central relational database or to service-specific databases where necessary.
Frontend: A single-page application (SPA) built with React.js to provide responsive interfaces that work across a range of devices. The frontend communicates with backend services through an API gateway.
API Gateway: Central point for routing, authentication, rate limiting and request aggregation. An API gateway simplifies client interactions and consolidates cross-cutting concerns such as authentication and logging.
Service Mesh and Orchestration: Kubernetes is used to orchestrate containerized services. A service mesh (for example, Istio) can be introduced to manage inter-service communication, observability, and security. Kubernetes enables deployment across multiple availability zones for resilience.
Data Storage: PostgreSQL is the principal data store due to its transactional guarantees and mature replication features. For certain event or audit logs, an append-only log or a document store may be used. Caching (for example, Redis) is recommended for session management and frequently accessed read-only data.
Event Bus: An event-driven component (for instance, Kafka) is recommended to handle asynchronous workflows such as scheduled contributions, payout triggers, notifications and audit trail propagation. The event bus supports decoupling of services and provides resilience through durable log storage.
Smart Contracts: Smart contracts are proposed as an optional component for enforcing payout rules in an immutable manner. A hybrid approach is advised: implement core functionality in cloud services while offering smart contract integration as an opt-in module for groups that prefer on-chain transparency.
Monitoring and Observability: Prometheus and Grafana are recommended for metric collection and visualization. Distributed tracing (for example, Jaeger) and centralized logging (for instance, ELK stack) provide additional visibility.
Security: Transport Layer Security (TLS) is required for all external communication. Authentication can use OAuth 2.0 or JWTs. Role-based access control and input validation are essential to reduce the attack surface and prevent common vulnerabilities.
7. Technology Stack and Tools
The following technology stack is recommended for Mbole Pay:
Frontend
- React.js: For building a responsive single-page application.
- Tailwind CSS or equivalent: For rapid UI development and consistent styling.
Backend
- Node.js with Express or NestJS: For modular, asynchronous REST APIs.
- PostgreSQL: Primary relational database for transactional data.
- Redis: For caching and fast session management.
Infrastructure and DevOps
- Docker: Containerization of services.
- Kubernetes: Container orchestration and scaling.
- Helm: Manage Kubernetes deployments.
- Jenkins or GitHub Actions: CI/CD pipelines for automated build, test and deployment.
Messaging and Eventing – Apache Kafka or RabbitMQ: For event-driven workflows and asynchronous tasks.
Monitoring and Logging – Prometheus and Grafana: Metrics collection and visualization.
- ELK Stack (Elasticsearch, Logstash, Kibana): Centralized logging and search.
Security
- OAuth 2.0 / OpenID Connect: Authentication and authorization flows.
- TLS for transport encryption.
- JWT tokens for stateless session management.
Optional
- Solidity and Truffle/Hardhat: For smart contract development and testing.
- IPFS: For decentralized storage of non-sensitive documents or receipts.
8. Non-Functional Requirements: Scalability, Fault Tolerance, Collaboration
Mbole Pay must satisfy several non-functional requirements that are critical for user trust and system robustness.
Scalability: The system must handle growth in the number of users and groups. Horizontal scaling of stateless services and database replication are planned to meet demand. Kubernetes autoscaling policies will be configured to respond to load.
Fault Tolerance and High Availability: Services should be deployed across multiple availability zones. Replication, redundant instances, and automated failover mechanisms are necessary to maintain uptime during outages. Backups and disaster recovery plans must be in place.
Consistency and Integrity: Financial data requires strong consistency for certain operations (contribution recording, payout execution). The platform will use transactional semantics in PostgreSQL for critical operations and idempotent design for distributed workflows.
Security: Authentication, authorization, encryption, secure secrets management and audit logging must be enforced. Regular security reviews and vulnerability scans should be part of the development lifecycle.
Usability and Accessibility: The user interface must be simple, support multiple languages and be usable on low-bandwidth devices. Offline support through progressive web app features can be considered for intermittent connectivity scenarios.
Maintainability: Clear service boundaries, consistent code style, extensive test coverage and automated deployments will improve maintainability.
9. Implementation Plan
The implementation plan is organized into phases aligned with an academic timetable and a target completion date in February 2026. The plan follows Agile principles with weekly sprints and defined deliverables for each phase.
Phase 1: Project Initiation (October 2025)
- Finalize requirements and use cases.
- Prepare project repository and initial CI/CD scaffolding.
- Design user interface mockups and wireframes.
Phase 2: Frontend Development (November 2025)
- Implement SPA with React.js: user registration, group creation, contribution views and basic client-side validation.
- Implement responsive design and accessibility features.
Phase 3: Backend and API Development (December 2025)
- Implement core backend services (authentication, group management, contribution service).
- Define database schema and implement initial migrations.
- Integration of basic notification service for reminders.
Phase 4: Integration and Smart Contract Prototyping (January 2026)
- Integrate frontend with backend APIs.
- Develop event-driven workflows for scheduled contributions and payouts.
- Prototype smart contract logic on a test network.
Phase 5: Testing, Deployment and Documentation (February 2026)
- Perform unit, integration and end-to-end testing.
- Deploy services to a staging environment with Kubernetes.
- Finalize documentation and prepare the final report and presentation.
Each phase will incorporate sprint reviews, retrospectives and user feedback where possible.
10. Calendar of Activities (October 2025 - February 2026)
The calendar below outlines weekly activities from October 2025 through February 2026. All dates are approximate and presented for planning purposes.
October 2025
Week 1 (Oct 1 - Oct 7): Project kickoff, requirement gathering, literature synthesis.
Week 2 (Oct 8 - Oct 14): Finalize scope, produce initial wireframes and UX flows.
Week 3 (Oct 15 - Oct 21): Set up repository, CI/CD basic pipeline, and project documentation template.
Week 4 (Oct 22 - Oct 31): Review and approval of design, begin frontend scaffolding.
November 2025
Week 1 (Nov 1 - Nov 7): Implement user authentication and registration UI.
Week 2 (Nov 8 - Nov 14): Build group creation and listing components.
Week 3 (Nov 15 - Nov 21): Implement contribution forms and history views.
Week 4 (Nov 22 - Nov 30): Responsive design adjustments and accessibility checks.
December 2025
Week 1 (Dec 1 - Dec 7): Backend service scaffolding and database schema design.
Week 2 (Dec 8 - Dec 14): Implement authentication and user profile endpoints.
Week 3 (Dec 15 - Dec 21): Implement group management and contribution endpoints.
Week 4 (Dec 22 - Dec 31): Integration testing and holiday buffer.
January 2026
Week 1 (Jan 1 - Jan 7): Event bus setup and scheduled tasks for payouts.
Week 2 (Jan 8 - Jan 14): Smart contract prototyping on testnet; integrate with backend simulation.
Week 3 (Jan 15 - Jan 21): Notification service and audit logging.
Week 4 (Jan 22 - Jan 31): End-to-end testing and performance tuning.
February 2026
Week 1 (Feb 1 - Feb 7): Final deployment to staging; security audit and user acceptance testing.
Week 2 (Feb 8 - Feb 14): Prepare the final report, presentation slides and demo scripts.
Week 3 (Feb 15 - Feb 21): Project submission and presentation rehearsal.
Week 4 (Feb 22 - Feb 28): Submit final deliverables and project archival.


11. Expected Outcomes
The expected outcomes of the Mbole Pay project include the following deliverables:
A functional frontend prototype that demonstrates the user journey for creating and managing Njangi groups, recording contributions and viewing payout schedules.
A complete project report with architecture design, implementation plan, risk assessment and references suitable for academic evaluation.
A project repository with initial CI/CD configuration, frontend source code and documentation to support future backend integration.
A prototype smart contract that demonstrates how payout and dispute resolution logic could be enforced on a blockchain testnet.
Recommendations and a roadmap for future work including backend development, payment integrations and production deployment strategies.
12. Conclusion and Recommendations
Mbole Pay proposes a pragmatic and culturally sensitive approach to digitizing Njangi systems. The design balances practical constraints with modern distributed systems principles, offering a cloud-first microservices architecture with optional on-chain components for increased transparency. The implementation plan and calendar are feasible within the stated timeline for an undergraduate project, provided disciplined sprint execution and periodic stakeholder feedback. The recommendations include prioritizing backend development, ensuring security best practices, performing load and failover testing, and engaging with potential user groups for usability testing and adoption studies. Long-term considerations include formal integration with mobile money providers, compliance with financial regulations in target jurisdictions, and exploring partnerships with local community organizations to promote adoption.
13. References
References
Aker, J. C., Boumnijel, R., McClellan, C., & Tierney, N. (2016). 'Paying for Prediction: The Case for Digital Financial Services in Development.' Journal of Development Economics, 123, 1-13.
Catalini, C., & Gans, J. S. (2016). 'Some Simple Economics of the Blockchain.' MIT Sloan Research Paper.
Newman, S. (2015). 'Building Microservices: Designing Fine-Grained Systems.' O'Reilly Media.
World Bank. (2018). 'Financial Inclusion in Africa: Trends and Challenges.' World Bank Publications.
Munyegera, G. K., & Matsumoto, T. (2016). 'Mobile Money, Bank Deposit and Loan Services: Evidence from Tanzania.' Journal of African Economies, 25(5), 702–723.
Esusu. (2020). 'Digital Savings and Lending Solutions.' Company whitepaper and product documentation.
Hardt, D. (2019). 'A Practical Guide to Distributed Systems.' ACM Computing Surveys.
