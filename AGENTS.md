# AGENTS.md

## Project Overview

This agent is designed to handle both the backend and frontend scalability of the project. It will seamlessly integrate a chatbot into the existing system, utilizing Retrieval-Augmented Generation (RAG) techniques.

## Frontend

- **Framework**: Next.js
- **Scalability**: The agent will ensure that the frontend components are scalable, maintainable, and optimized for performance.

## Backend

- **Framework**: FastAPI
- **Scalability**: The agent will manage backend scalability, ensuring that APIs are efficient, maintainable, and capable of handling increased load.

## Chatbot Integration

- **Stack**: The chatbot will utilize **RAG (Retrieval-Augmented Generation)** techniques, combining powerful language models with relevant external data retrieval.
- **Purpose**: This approach ensures that the chatbot provides accurate, contextually relevant responses by fetching data on-demand.
- **Integration**: The agent will integrate the RAG stack seamlessly, ensuring that the chatbot leverages both the existing project data and real-time information.

## Code Style and Best Practices

- Follow **TypeScript strict mode** for the frontend.
- Use **Pydantic models** and **async programming** for the backend.
- Ensure modular, well-documented, and convention-compliant code.

## Security Considerations

- Never hardcode sensitive information.
- Use environment variables for credentials.
- Sanitize user inputs and validate data on both frontend and backend.

## Scalability and Maintenance

- The agent should ensure that both frontend and backend are scalable, allowing easy addition or removal of features.

## RAG Integration

- **Purpose**: The chatbot will utilize **RAG** techniques to enhance its responses.
- **Functionality**: It will retrieve relevant data from external sources before generating responses, ensuring more accurate and context-aware answers.
- **Integration**: The agent will seamlessly incorporate the RAG stack, making sure that the chatbot is both dynamic and responsive.


