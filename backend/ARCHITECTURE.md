"""Architecture and Design Documentation.

This file documents the architecture, design patterns, and key decisions
in the LoanAI multi-agent loan processing system.
"""

"""
## Architecture Overview

### System Design Principles

1. **Modularity**: Each agent is independent and can be extended
2. **Asynchrony**: Non-blocking concurrent processing
3. **Separation of Concerns**: Clear boundaries between components
4. **Error Handling**: Comprehensive exception handling
5. **Logging**: Detailed logging for debugging and monitoring
6. **Type Safety**: Full type hints throughout codebase

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API/Demo Interface                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │   LoanApplicationProcessor (Main Orchestrator)       │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│    ┌────────────┼────────────┐                              │
│    │            │            │                              │
│    ▼            ▼            ▼                              │
│ ┌─────────┐ ┌────────┐ ┌──────────────┐                    │
│ │Loan     │ │Bank    │ │Salary        │ ┌──────────────┐  │
│ │Officer  │ │Statement│Statement     │ │Verification  │  │
│ │Agent    │ │Agent    │Agent         │ │Agent (MCP)   │  │
│ └─────────┘ └────────┘ └──────────────┘ └──────────────┘  │
│    │            │            │               │              │
│    └────────────┼────────────┼───────────────┘              │
│                 │                                            │
│    ┌────────────▼────────────────────────────┐              │
│    │  AgentCommunicationHub                  │              │
│    │  - Message passing                      │              │
│    │  - Deliberation coordination            │              │
│    │  - Consensus building                   │              │
│    └────────────┬────────────────────────────┘              │
│                 │                                            │
│    ┌────────────▼──────────────────────────────────┐        │
│    │  Decision Framework                          │        │
│    │  - Risk Scoring Engine                       │        │
│    │  - Decision Engine                           │        │
│    │  - Loan Terms Calculator                     │        │
│    └──────────────────────────────────────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Loan Application Input
         │
         ▼
┌─────────────────────┐
│  Phase 1: Analysis  │  Run agents in parallel
│  - Bank Analysis    │
│  - Salary Analysis  │  Each agent produces:
│  - Verification    │  - Risk Score
│                     │  - Confidence Score
└────────────┬────────┘  - Recommendation
             │
             ▼
┌─────────────────────────────────────┐
│  Phase 2: Deliberation              │  Agents discuss findings
│  - Share findings                   │  Identify agreements/disagreements
│  - Discuss concerns                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Phase 3: Consensus Building        │  Aggregate opinions
│  - Vote on recommendation           │  Calculate final metrics
│  - Calculate consensus score        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Phase 4: Final Decision            │  Loan Officer decides
│  - Risk Assessment                  │  Calculate loan terms
│  - Apply decision logic             │
│  - Generate explanation             │
└────────────┬────────────────────────┘
             │
             ▼
Decision Result (APPROVED/REJECTED/MANUAL_REVIEW)
```

### Key Design Decisions

#### 1. **Async-First Architecture**
- All heavy operations are async
- Enables parallel processing of independent tasks
- Better resource utilization
- Scalable for handling multiple applications

```python
# Example: Parallel agent analysis
tasks = {
    'bank': asyncio.create_task(bank_agent.analyze(app)),
    'salary': asyncio.create_task(salary_agent.analyze(app)),
    'verification': asyncio.create_task(verification_agent.analyze(app)),
}
results = await asyncio.gather(*tasks.values())
```

#### 2. **Agent Base Classes**
- All agents inherit from `BaseAgent`
- Provides common interface and utilities
- Specialized subclasses: `AnalysisAgent`, `DecisionAgent`
- Easy to add new agent types

#### 3. **Type-Safe Models**
- Pydantic models for all data structures
- Automatic validation
- Clear data contracts
- IDE auto-completion support

```python
# Pydantic ensures valid data
application = LoanApplication(
    customer_id="123",
    personal_info=PersonalInfo(...),  # Validates nested objects
    loan_request=LoanRequest(...),     # Ensures loan_amount > 0, etc.
)
```

#### 4. **Communication Hub Pattern**
- Central coordinator for agent messages
- Message history tracking
- Deliberation facilitation
- Consensus calculation

#### 5. **Risk Scoring Framework**
- Weighted scoring from multiple factors
- Configurable thresholds
- Clear decision boundaries
- Explainable risk assessment

#### 6. **Tool Integration**
- Pluggable tools for agents
- Document processing, financial analysis, verification
- Can be extended with additional tools
- Simulated for demo (ready for real implementations)

## Code Organization

### Package Structure

```
loanai_agent/
├── agents/              # Agent implementations
│   ├── base_agent.py   # Abstract base classes
│   ├── loan_officer.py # Orchestrator agent
│   ├── bank_statement.py
│   ├── salary_statement.py
│   └── verification.py
├── models/              # Data models
│   ├── schemas.py      # Application data models
│   └── decision.py     # Decision-related enums
├── protocols/           # Communication & decisions
│   ├── communication.py # Agent communication hub
│   └── decision_engine.py # Risk scoring & decisions
├── tools/               # Agent tools
│   ├── analysis_tools.py
│   ├── verification_tools.py
│   └── document_processor.py
└── utils/               # Utilities
    ├── logger.py       # Logging setup
    ├── exceptions.py   # Custom exceptions
    └── helpers.py      # Helper functions
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `BankStatementAgent`)
- **Functions**: snake_case (e.g., `calculate_risk_score`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DECISION_THRESHOLD_APPROVE`)
- **Files**: snake_case.py (e.g., `bank_statement.py`)
- **Private methods**: _snake_case (e.g., `_perform_analysis`)

### Error Handling Strategy

```
┌─────────────────────────────────────────────┐
│  Custom Exception Hierarchy                 │
├─────────────────────────────────────────────┤
│  LoanAIException (base)                     │
│  ├── AgentException                         │
│  ├── CommunicationException                 │
│  ├── ConsensusException                     │
│  ├── DocumentProcessingException            │
│  ├── VerificationException                  │
│  ├── DecisionException                      │
│  ├── ValidationException                    │
│  ├── TimeoutException                       │
│  └── ConfigurationException                 │
└─────────────────────────────────────────────┘
```

## Processing Pipeline Details

### Agent Analysis Phase

Each agent:
1. Receives loan application
2. Extracts relevant data
3. Performs specialized analysis
4. Generates confidence score (0-1)
5. Calculates risk score (0-100)
6. Provides recommendation (approve/reject/review)
7. Returns detailed reasoning

### Deliberation Phase

Agents:
1. Share analysis findings with each other
2. Discuss disagreements
3. Present supporting evidence
4. May adjust recommendations based on discussions
5. Consensus emerges through multiple rounds

### Decision Phase

Loan Officer:
1. Reviews all agent analyses
2. Calculates aggregate risk
3. Applies decision logic:
   - Risk < 40: APPROVED
   - Risk 40-60: MANUAL_REVIEW
   - Risk > 60: REJECTED
4. Checks override conditions
5. Calculates loan terms
6. Generates explanation

## Extensibility Points

### Adding New Agents

1. Create class inheriting from `AnalysisAgent`
2. Implement `_perform_analysis()` method
3. Return analysis dict with required fields
4. Register in communication hub

```python
class CustomAgent(AnalysisAgent):
    async def _perform_analysis(self, app, **kwargs):
        # Custom analysis logic
        return {
            'confidence_score': 0.85,
            'risk_score': 35,
            'recommendation': 'approve',
            'reasoning': 'Analysis result'
        }
```

### Adding New Tools

1. Create tool class in `tools/`
2. Implement static methods for operations
3. Return structured results
4. Add to agent's tools list

### Custom Decision Logic

1. Extend `DecisionEngine`
2. Override `make_decision()` method
3. Implement custom rules
4. Return `DecisionStatus`

## Performance Considerations

### Optimization Strategies

1. **Parallel Processing**: All sub-agent analyses run concurrently
2. **Lazy Evaluation**: Analysis only performed for submitted documents
3. **Caching**: Results cached during deliberation rounds
4. **Timeouts**: Configurable timeouts for long operations
5. **Early Exit**: Stop processing on critical fraud detection

### Scalability

- **Async**: Non-blocking I/O for handling multiple applications
- **Distributed Ready**: Architecture supports distributed deployment
- **Horizontal Scaling**: Can run multiple processors in parallel
- **Load Distribution**: Agent work can be distributed across nodes

## Testing Strategy

### Test Coverage

- **Unit Tests**: Individual component testing
- **Integration Tests**: Agent interaction testing
- **Scenario Tests**: Real-world application scenarios
- **Mock Data**: Realistic test data in conftest.py

### Testing Best Practices

1. Use fixtures for common test data
2. Mock external dependencies
3. Test both happy paths and error cases
4. Validate error messages
5. Ensure async operations work correctly

## Future Enhancements

1. **Real Document Processing**: Integrate with Google Document AI
2. **Real Web Verification**: Connect to actual web search APIs
3. **Database Integration**: Persist decisions to Cloud SQL
4. **API Endpoints**: REST/GraphQL API wrapper
5. **Dashboard**: Web UI for monitoring decisions
6. **A/B Testing**: Compare agent configurations
7. **Machine Learning**: Train models on decision outcomes
8. **Compliance Reporting**: Generate compliance reports
9. **Audit Trail**: Complete audit logging
10. **Multi-language**: Support multiple languages

## References

- Google ADK Documentation: https://cloud.google.com/adk
- Pydantic Documentation: https://docs.pydantic.dev/
- Python async/await: https://docs.python.org/3/library/asyncio.html
- Design Patterns: https://refactoring.guru/design-patterns
"""
