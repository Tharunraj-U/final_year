---
title: 'CodeMaster AI: An Intelligent Adaptive Learning Platform for Programming Education'
tags:
  - Python
  - JavaScript
  - React
  - artificial intelligence
  - programming education
  - intelligent tutoring system
  - adaptive learning
  - LLM
authors:
  - name: Tharun Raj U
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Department of Computer Science, Institution Name, Country
    index: 1
date: 13 March 2026
bibliography: paper.bib
---

# Summary

**CodeMaster AI** is an open-source intelligent tutoring system designed to provide personalized programming education through adaptive learning techniques and AI-powered code analysis. The platform combines a hybrid AI architecture—integrating rule-based algorithms with Large Language Models (OpenAI GPT-4 and local Ollama models)—to deliver real-time feedback, personalized problem recommendations, and interactive tutoring for learners at all skill levels.

The system features over 200 curated coding problems spanning multiple data structures and algorithms (arrays, strings, linked lists, trees, graphs, dynamic programming), a sophisticated multi-factor scoring mechanism, and an adaptive recommendation engine that dynamically adjusts to individual learning patterns and demonstrated mastery levels.

# Statement of Need

The global demand for software developers continues to grow, with projections indicating a 25% increase in software development positions by 2031. Traditional programming education methods often fail to address diverse learning needs, while existing platforms like LeetCode and HackerRank lack truly personalized learning paths and intelligent feedback mechanisms.

CodeMaster AI addresses these gaps by providing:

- **Personalized Recommendations**: A hybrid AI system analyzes user performance across topic categories, difficulty levels, and learning velocity to suggest optimally challenging problems
- **Intelligent Code Analysis**: AI-powered evaluation of time complexity, space complexity, code quality, and algorithmic approach
- **Adaptive Difficulty Progression**: Dynamic adjustment based on demonstrated mastery using zone-of-proximal-development principles
- **Interactive AI Tutoring**: Multi-level hint system with contextual assistance powered by LLMs
- **Cost-Effective Deployment**: Dual-mode AI support (cloud OpenAI API or free local Ollama inference) ensuring accessibility for educational institutions

The platform serves computer science students, self-learners, coding bootcamp participants, and educational institutions seeking intelligent tutoring capabilities without expensive licensing costs.

# Architecture

CodeMaster AI employs a three-tier architecture:

- **Frontend**: React.js application with Monaco code editor, real-time syntax highlighting, and responsive dashboard components
- **Backend**: Flask-based REST API handling code execution, performance analysis, recommendation generation, and AI service orchestration
- **AI Layer**: Hybrid system supporting OpenAI GPT-4 for cloud deployment or Ollama with qwen2.5-coder for local, cost-free inference

The recommendation engine implements a multi-factor scoring algorithm considering:
$$R_{score} = w_1 \cdot T_{weakness} + w_2 \cdot D_{appropriate} + w_3 \cdot V_{variety} + w_4 \cdot S_{streak}$$

Where $T_{weakness}$ represents topic weakness priority, $D_{appropriate}$ indicates difficulty appropriateness, $V_{variety}$ ensures problem diversity, and $S_{streak}$ accounts for learning momentum.

# Key Features

- **200+ Coding Problems**: Comprehensive problem bank covering fundamental and advanced algorithms
- **Real-time Code Execution**: Secure sandboxed execution with test case validation
- **Performance Analytics**: Detailed dashboards showing progress, strengths, and areas for improvement
- **Gamification Elements**: Achievement system, streak tracking, and leaderboards to enhance engagement
- **Google OAuth Integration**: Seamless authentication for user management
- **Weekly Progress Reports**: Automated email reports summarizing learning progress

# Acknowledgements

This software was developed as part of a final year academic project. We acknowledge the open-source community for the foundational libraries and frameworks that made this project possible.

# References
