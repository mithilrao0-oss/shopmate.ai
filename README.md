# ShopMate.ai — AI-Powered Product Discovery & Auto-Content Platform

## 1. Project Overview

ShopMate.ai is a college Semester 5 AIOT project that aims to simplify product discovery and marketing for dropshipping businesses using AI agents.

The platform is designed to help users discover suitable products, identify emerging trend signals, generate marketing content, and review content before publication.

The project focuses on using Generative AI, prompt engineering, and agent-based workflows to assist with product discovery and content creation.

## 2. Problem Statement

Dropshipping businesses often need to spend considerable time researching products, monitoring trends, and creating promotional content.

ShopMate.ai aims to organize and simplify these activities through an AI-assisted workflow.

## 3. Main Objectives

* Collect and organize product information.
* Filter products using defined criteria.
* Identify potential trends using available engagement and product data.
* Generate product descriptions, captions, and promotional scripts using an LLM.
* Support the creation of short-form promotional content.
* Provide a dashboard for viewing products, trends, and generated content.
* Include a human review step before content is published.

## 4. Proposed Features

### Product Discovery

The platform is designed to collect product information and filter products according to selected criteria.

### Trend Insights

The trend workflow aims to surface products showing potentially useful signals, such as engagement changes or other available indicators.

Trend insights are not guaranteed predictions of virality or product success.

### AI Content Generation

An LLM will be used to assist with generating marketing content, such as:

* Product descriptions
* Social media captions
* Promotional video scripts
* Voiceover text

### Content Review

Generated content will be presented for human review before publication.

### Dashboard

The frontend provides a dashboard intended to help users navigate product discovery, trend insights, AI-generated content, and the review workflow.

## 5. Technology Stack

The planned technology stack includes:

| Component                   | Technology          |
| --------------------------- | ------------------- |
| Frontend                    | React               |
| Frontend development server | Vite                |
| Backend API                 | Python with FastAPI |
| AI workflows                | Python-based agents |
| Language model              | Open-source LLM     |
| Database                    | SQLite              |
| Version control             | Git and GitHub      |

The stack and architecture may be adjusted as development progresses.

## 6. Current Development Status

### Completed

* Created the initial project scaffold.
* Set up the React frontend using Vite.
* Created the initial ShopMate.ai dashboard interface.
* Added dashboard sections for product discovery, trend insights, AI content, and review workflow.
* Added sample product and dashboard information for demonstration.
* Initialized and updated the GitHub repository.

### In Progress

* Making dashboard navigation interactive.
* Developing the individual frontend pages.
* Implementing the backend API.
* Developing the product sourcing and filtering workflow.
* Developing the trend analysis workflow.
* Integrating the LLM for content generation.

### Planned

* Connect the frontend to the backend.
* Store and retrieve product information using SQLite.
* Connect the AI agents to the application workflow.
* Develop the content-generation pipeline.
* Add a human approval workflow.
* Investigate platform integrations, subject to API access and platform requirements.

**Note:** The dashboard currently uses demonstration data. The backend, AI agents, database integration, and external publishing features should not be considered operational until implemented and tested.

## 7. System Workflow

The proposed workflow is:

1. Collect product information.
2. Filter and organize products.
3. Analyze available data for trend signals.
4. Generate marketing content using an LLM.
5. Present the generated content for human review.
6. Allow approved content to proceed to the next publishing step, when supported.

## 8. Responsible AI

ShopMate.ai is intended to follow responsible AI practices:

* Clearly identify demonstration data and generated content.
* Avoid presenting trend signals as guaranteed predictions.
* Keep a human approval step before publication.
* Review generated content for accuracy and suitability.
* Respect supplier terms and third-party platform requirements.
* Protect API keys and other credentials using environment variables.

## 9. Project Scope and Limitations

This project is being developed as a manageable college AIOT application.

The initial version focuses on demonstrating an AI-assisted workflow rather than providing a fully autonomous commercial dropshipping service.

Real supplier data, trend data, LLM services, and social media publishing may require external accounts, API access, credentials, and additional testing.

The availability and reliability of these integrations will depend on the services used.

## 10. Academic Relevance

The project is intended to demonstrate concepts related to:

* Foundations of Generative AI and Large Language Models
* Prompt Engineering
* Agentic AI and Autonomous Systems
* AI-assisted application development
* Responsible AI practices

## 11. Future Improvements

Possible future improvements include:

* Additional product filtering options.
* More detailed trend visualizations.
* Improved content-generation prompts.
* Better content review and approval controls.
* Additional integrations where API access is available.

## 12. Repository

GitHub repository:

https://github.com/mithilrao0-oss/shopmate.ai

## 13. Disclaimer

ShopMate.ai is an academic project. Product examples and dashboard metrics may be illustrative demonstration data and should not be interpreted as verified market research or guaranteed business outcomes.
