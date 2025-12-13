
## 3. Data Flow & Communication

### 3.1 Agent Communication Protocol

**Message Structure**:
```python
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    ANALYSIS_RESULT = "analysis_result"
    CLARIFICATION_REQUEST = "clarification_request"
    CONSENSUS_VOTE = "consensus_vote"
    FINAL_DECISION = "final_decision"

@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: dict
    timestamp: str
    correlation_id: str  # Links all messages for one application
```

### 3.2 Communication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: TASK DISTRIBUTION                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Loan Officer ──[Task: Analyze Bank Statement]──> Bank Agent   │
│              ──[Task: Analyze Salary Slip]────> Salary Agent   │
│              ──[Task: Verify External Data]───> Verification   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: PARALLEL ANALYSIS                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Bank Agent      ──> [Analyzing transactions...]               │
│  Salary Agent    ──> [Extracting employment data...]           │
│  Verification    ──> [Searching web, APIs...]                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: CROSS-AGENT DELIBERATION                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Bank Agent ←─────────────────────────────────────────────────→ │
│      ↕                                                          │
│  Salary Agent ←───────[Share findings & discuss]───────────────→│
│      ↕                                                          │
│  Verification Agent ←─────────────────────────────────────────→ │
│                                                                 │
│  Topics:                                                        │
│  • Salary consistency between documents                        │
│  • Employment verification cross-check                         │
│  • Income vs market benchmarks                                 │
│  • Any discrepancies or concerns                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4: CONSENSUS BUILDING                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Each Agent Submits:                                           │
│  • Recommendation (Approve/Reject/Review)                      │
│  • Confidence Score (0-1)                                      │
│  • Risk Score (0-100)                                          │
│  • Key Findings                                                │
│  • Concerns or Red Flags                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5: FINAL DECISION BY LOAN OFFICER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Loan Officer Reviews:                                         │
│  • All sub-agent reports                                       │
│  • Discussion transcripts                                      │
│  • Consensus recommendation                                    │
│  • Aggregate risk score                                        │
│                                                                 │
│  Makes Final Decision:                                         │
│  • APPROVED / REJECTED / MANUAL_REVIEW                         │
│  • Loan amount (may adjust)                                    │
│  • Interest rate recommendation                                │
│  • Conditions (if any)                                         │
│  • Detailed explanation                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Implementation: Agent Communication

```python
from google.adk import AgentOrchestrator, CommunicationProtocol

class LoanApplicationOrchestrator:
    def __init__(self):
        self.loan_officer = Agent(loan_officer_config)
        self.bank_agent = Agent(bank_statement_config)
        self.salary_agent = Agent(salary_statement_config)
        self.verification_agent = Agent(verification_config)
        
        # Setup communication channels
        self.protocol = CommunicationProtocol(
            agents=[
                self.loan_officer,
                self.bank_agent,
                self.salary_agent,
                self.verification_agent
            ],
            enable_peer_communication=True,
            enable_group_discussion=True
        )
    
    async def process_application(self, customer_id: str):
        # Phase 1: Load customer data
        customer_data = await load_customer_data(customer_id)
        
        # Phase 2: Parallel analysis
        tasks = [
            self.bank_agent.analyze(customer_data),
            self.salary_agent.analyze(customer_data),
            self.verification_agent.verify(customer_data)
        ]
        
        sub_agent_results = await asyncio.gather(*tasks)
        
        # Phase 3: Agent deliberation
        discussion_result = await self.protocol.group_discussion(
            participants=[self.bank_agent, self.salary_agent, self.verification_agent],
            topic="Loan Application Analysis",
            context={
                "customer_data": customer_data,
                "individual_results": sub_agent_results
            },
            max_rounds=3
        )
        
        # Phase 4: Consensus
        consensus = await self.protocol.build_consensus(
            agents=[self.bank_agent, self.salary_agent, self.verification_agent],
            results=sub_agent_results,
            discussion=discussion_result
        )
        
        # Phase 5: Final decision
        final_decision = await self.loan_officer.make_decision(
            customer_data=customer_data,
            sub_agent_results=sub_agent_results,
            discussion_transcript=discussion_result,
            consensus=consensus
        )
        
        return final_decision
```

---

## 4. Implementation with Google ADK

### 4.1 Project Structure

```
loanai-agent-system/
├── agents/
│   ├── __init__.py
│   ├── loan_officer.py          # Main orchestrator agent
│   ├── bank_statement_agent.py  # Bank statement analyzer
│   ├── salary_agent.py          # Salary verification agent
│   └── verification_agent.py    # MCP-enabled verification
├── tools/
│   ├── __init__.py
│   ├── ocr_tools.py             # Document AI integration
│   ├── analysis_tools.py        # Financial analysis functions
│   └── verification_tools.py    # Web search & API tools
├── mcp/
│   ├── __init__.py
│   ├── mcp_config.json          # MCP server configuration
│   └── mcp_tools.py             # MCP tool wrappers
├── protocols/
│   ├── __init__.py
│   ├── communication.py         # Agent communication protocol
│   └── consensus.py             # Consensus mechanism
├── models/
│   ├── __init__.py
│   ├── schemas.py               # Data models
│   └── decision_models.py       # Decision framework models
├── config/
│   ├── agent_config.yaml        # Agent configurations
│   └── mcp_servers.json         # MCP server settings
├── main.py                      # Entry point
├── requirements.txt
└── README.md
```

### 4.2 Core Implementation Files

#### 4.2.1 Main Orchestrator (`main.py`)

```python
import asyncio
from google.adk import initialize_adk
from agents.loan_officer import LoanOfficerAgent
from agents.bank_statement_agent import BankStatementAgent
from agents.salary_agent import SalaryAgent
from agents.verification_agent import VerificationAgent
from protocols.communication import AgentCommunicationHub
from models.schemas import LoanApplication, DecisionResult

# Initialize Google ADK
initialize_adk(
    project_id="loanai-production",
    credentials_path="./config/gcp-credentials.json"
)

class LoanApplicationProcessor:
    def __init__(self):
        # Initialize agents
        self.loan_officer = LoanOfficerAgent()
        self.bank_agent = BankStatementAgent()
        self.salary_agent = SalaryAgent()
        self.verification_agent = VerificationAgent()
        
        # Setup communication hub
        self.comm_hub = AgentCommunicationHub([
            self.loan_officer,
            self.bank_agent,
            self.salary_agent,
            self.verification_agent
        ])
    
    async def process(self, application: LoanApplication) -> DecisionResult:
        """
        Process a loan application through the multi-agent system
        """
        print(f"Processing application: {application.customer_id}")
        
        # Step 1: Distribute tasks to sub-agents
        tasks = {
            'bank_analysis': self.bank_agent.analyze_bank_statement(
                application.documents.bank_statement_path,
                application.employment.monthly_salary
            ),
            'salary_analysis': self.salary_agent.analyze_salary_statement(
                application.documents.salary_statement_path,
                application.employment
            ),
            'verification': self.verification_agent.verify_information(
                application.education,
                application.employment,
                application.personal_info
            )
        }
        
        # Execute in parallel
        results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        analysis_results = dict(zip(tasks.keys(), results))
        
        # Step 2: Inter-agent deliberation
        deliberation = await self.comm_hub.facilitate_discussion(
            topic="Application Risk Assessment",
            context=analysis_results,
            participants=[self.bank_agent, self.salary_agent, self.verification_agent],
            max_rounds=3
        )
        
        # Step 3: Build consensus
        consensus = await self.comm_hub.build_consensus(
            analysis_results=analysis_results,
            deliberation_transcript=deliberation
        )
        
        # Step 4: Loan Officer makes final decision
        final_decision = await self.loan_officer.make_decision(
            application=application,
            sub_agent_results=analysis_results,
            deliberation=deliberation,
            consensus=consensus
        )
        
        # Step 5: Store decision in database
        await self.save_decision(application.customer_id, final_decision)
        
        return final_decision
    
    async def save_decision(self, customer_id: str, decision: DecisionResult):
        """Save decision to Cloud SQL"""
        # Implementation here
        pass

# Main execution
async def main():
    processor = LoanApplicationProcessor()
    
    # Example: Process application
    application = await load_application_from_db("customer-uuid-123")
    result = await processor.process(application)
    
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Explanation: {result.explanation}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 4.2.2 Bank Statement Agent (`agents/bank_statement_agent.py`)

```python
from google.adk import Agent, Tool
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from typing import Dict, Any
import json
from dataclasses import dataclass

@dataclass
class BankAnalysisResult:
    confidence_score: float
    average_balance: float
    monthly_income: float
    expense_ratio: float
    risk_score: int
    recommendation: str
    reasoning: str
    red_flags: list

class BankStatementAgent:
    def __init__(self):
        self.agent = Agent(
            name="bank_statement_agent",
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            system_prompt=self._get_system_prompt(),
            tools=[
                Tool(name="extract_text", function=self.extract_document_text),
                Tool(name="analyze_transactions", function=self.analyze_transactions),
                Tool(name="detect_fraud", function=self.detect_fraud_patterns),
                Tool(name="calculate_metrics", function=self.calculate_financial_metrics)
            ]
        )
        
        # Initialize Google Cloud services
        self.doc_ai_client = documentai.DocumentProcessorServiceClient()
        self.storage_client = storage.Client()
        
    def _get_system_prompt(self) -> str:
        return """You are an expert financial analyst specialized in bank statement analysis.
        
        Your responsibilities:
        1. Extract transaction data from bank statements
        2. Analyze income patterns and consistency
        3. Calculate financial health metrics
        4. Identify potential fraud or irregularities
        5. Assess lending risk
        
        Be thorough, analytical, and objective. Focus on:
        - Income stability and consistency
        - Expense management
        - Savings behavior
        - Debt obligations
        - Any red flags or concerns
        
        Provide confidence scores for your findings and clear reasoning."""
    
    async def analyze_bank_statement(
        self, 
        document_path: str, 
        self_reported_salary: float
    ) -> BankAnalysisResult:
        """
        Main entry point for bank statement analysis
        """
        # Step 1: Extract text from document using Document AI
        extracted_text = await self.extract_document_text(document_path)
        
        # Step 2: Parse transactions
        transactions = await self.parse_transactions(extracted_text)
        
        # Step 3: Analyze patterns
        analysis = await self.agent.run(
            prompt=f"""Analyze these bank transactions and provide detailed assessment:
            
            Extracted Data:
            {json.dumps(transactions, indent=2)}
            
            Self-reported monthly salary: ${self_reported_salary}
            
            Provide:
            1. Average monthly balance
            2. Total monthly income (from deposits)
            3. Total monthly expenses
            4. Income consistency score (0-100)
            5. Debt indicators
            6. Any red flags
            7. Comparison with self-reported salary
            8. Overall risk assessment
            9. Recommendation (approve/reject/review)
            10. Detailed reasoning
            """,
            tools=["analyze_transactions", "calculate_metrics", "detect_fraud"]
        )
        
        # Step 4: Structure the result
        result = self._structure_result(analysis, transactions)
        
        return result
    
    async def extract_document_text(self, gcs_path: str) -> str:
        """Extract text from PDF/Image using Document AI"""
        # Document AI processor
        processor_name = "projects/PROJECT_ID/locations/us/processors/PROCESSOR_ID"
        
        # Download document from GCS
        blob = self.storage_client.bucket("loanai-documents").blob(gcs_path)
        document_content = blob.download_as_bytes()
        
        # Process with Document AI
        request = documentai.ProcessRequest(
            name=processor_name,
            raw_document=documentai.RawDocument(
                content=document_content,
                mime_type="application/pdf"
            )
        )
        
        result = self.doc_ai_client.process_document(request=request)
        return result.document.text
    
    async def parse_transactions(self, text: str) -> Dict[str, Any]:
        """Parse transaction data from extracted text"""
        # Use Gemini to structure the transaction data
        response = await self.agent.run(
            prompt=f"""Extract all transactions from this bank statement text:
            
            {text}
            
            Return as JSON with this structure:
            {{
                "account_holder": "name",
                "account_number": "number",
                "statement_period": "start_date to end_date",
                "opening_balance": 0.0,
                "closing_balance": 0.0,
                "transactions": [
                    {{"date": "YYYY-MM-DD", "description": "...", "amount": 0.0, "type": "credit/debit"}}
                ]
            }}
            """
        )
        
        return json.loads(response.content)
    
    async def analyze_transactions(self, transactions: list) -> Dict[str, Any]:
        """Analyze transaction patterns"""
        # Calculate metrics
        credits = [t for t in transactions if t['type'] == 'credit']
        debits = [t for t in transactions if t['type'] == 'debit']
        
        total_credits = sum(t['amount'] for t in credits)
        total_debits = sum(t['amount'] for t in debits)
        
        # Identify recurring transactions
        recurring_income = self._identify_recurring(credits)
        recurring_expenses = self._identify_recurring(debits)
        
        return {
            "total_income": total_credits,
            "total_expenses": total_debits,
            "net_cashflow": total_credits - total_debits,
            "recurring_income": recurring_income,
            "recurring_expenses": recurring_expenses,
            "transaction_count": len(transactions)
        }
    
    def _identify_recurring(self, transactions: list) -> list:
        """Identify recurring transactions"""
        # Simple pattern matching - can be enhanced
        descriptions = {}
        for t in transactions:
            desc = t['description'].lower()
            if desc in descriptions:
                descriptions[desc].append(t['amount'])
            else:
                descriptions[desc] = [t['amount']]
        
        recurring = [
            {"description": desc, "frequency": len(amounts), "avg_amount": sum(amounts)/len(amounts)}
            for desc, amounts in descriptions.items()
            if len(amounts) >= 2
        ]
        
        return recurring
    
    async def detect_fraud_patterns(self, transactions: list) -> list:
        """Detect potential fraud indicators"""
        red_flags = []
        
        # Check for unusual patterns
        amounts = [t['amount'] for t in transactions]
        avg_amount = sum(amounts) / len(amounts)
        
        for t in transactions:
            # Large unusual transactions
            if t['amount'] > avg_amount * 5:
                red_flags.append({
                    "type": "unusual_large_transaction",
                    "transaction": t,
                    "severity": "medium"
                })
        
        # Check for round number patterns (potential fabrication)
        round_numbers = [t for t in transactions if t['amount'] % 100 == 0]
        if len(round_numbers) / len(transactions) > 0.8:
            red_flags.append({
                "type": "suspicious_round_numbers",
                "severity": "high",
                "description": "Too many round number transactions"
            })
        
        return red_flags
    
    def calculate_financial_metrics(self, analysis: Dict) -> Dict[str, float]:
        """Calculate key financial metrics"""
        return {
            "expense_to_income_ratio": analysis['total_expenses'] / analysis['total_income'],
            "savings_rate": (analysis['total_income'] - analysis['total_expenses']) / analysis['total_income'],
            "monthly_avg_balance": (analysis.get('opening_balance', 0) + analysis.get('closing_balance', 0)) / 2
        }
    
    def _structure_result(self, analysis: Any, transactions: Dict) -> BankAnalysisResult:
        """Convert analysis to structured result"""
        # Parse agent response and create result object
        # Implementation details...
        pass
```

#### 4.2.3 Agent Communication Hub (`protocols/communication.py`)

```python
from typing import List, Dict, Any
from google.adk import Agent
import asyncio
import json
from datetime import datetime

class AgentCommunicationHub:
    """
    Facilitates communication and deliberation between agents
    """
    def __init__(self, agents: List[Agent]):
        self.agents = {agent.name: agent for agent in agents}
        self.conversation_history = []
    
    async def facilitate_discussion(
        self,
        topic: str,
        context: Dict[str, Any],
        participants: List[Agent],
        max_rounds: int = 3
    ) -> Dict[str, Any]:
        """
        Facilitate a multi-round discussion between agents
        """
        discussion_log = {
            "topic": topic,
            "participants": [agent.name for agent in participants],
            "rounds": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Initial context sharing
        shared_context = self._prepare_context(context)
        
        for round_num in range(max_rounds):
            print(f"Discussion Round {round_num + 1}/{max_rounds}")
            
            round_messages = []
            
            for agent in participants:
                # Each agent reviews others' findings and provides input
                message = await self._get_agent_input(
                    agent,
                    topic,
                    shared_context,
                    discussion_log.get("rounds", [])
                )
                
                round_messages.append({
                    "agent": agent.name,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            discussion_log["rounds"].append({
                "round": round_num + 1,
                "messages": round_messages
            })
            
            # Check if consensus reached
            if self._check_early_consensus(round_messages):
                print(f"Consensus reached in round {round_num + 1}")
                break
        
        return discussion_log
    
    async def _get_agent_input(
        self,
        agent: Agent,
        topic: str,
        context: Dict,
        previous_rounds: List
    ) -> str:
        """Get agent's input for discussion"""
        
        prompt = f"""You are participating in a discussion about: {topic}
        
        Context:
        {json.dumps(context, indent=2)}
        
        Previous discussion rounds:
        {json.dumps(previous_rounds, indent=2)}
        
        Based on your analysis and considering other agents' perspectives:
        1. What are your key findings?
        2. Do you agree or disagree with other agents' assessments?
        3. Are there any concerns or risks you want to highlight?
        4. What is your recommendation?
        
        Respond concisely but thoroughly."""
        
        response = await agent.run(prompt=prompt)
        return response.content
    
    async def build_consensus(
        self,
        analysis_results: Dict[str, Any],
        deliberation_transcript: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build consensus from multiple agent results
        """
        # Extract recommendations
        recommendations = {}
        risk_scores = {}
        confidence_scores = {}
        
        for agent_name, result in analysis_results.items():
            recommendations[agent_name] = result.recommendation
            risk_scores[agent_name] = result.risk_score
            confidence_scores[agent_name] = result.confidence_score
        
        # Calculate weighted consensus
        total_confidence = sum(confidence_scores.values())
        weighted_risk = sum(
            risk * confidence_scores[agent] 
            for agent, risk in risk_scores.items()
        ) / total_confidence
        
        # Majority vote on recommendation
        rec_counts = {}
        for rec in recommendations.values():
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        consensus_recommendation = max(rec_counts, key=rec_counts.get)
        consensus_strength = rec_counts[consensus_recommendation] / len(recommendations)
        
        return {
            "consensus_recommendation": consensus_recommendation,
            "consensus_strength": consensus_strength,
            "weighted_risk_score": weighted_risk,
            "individual_recommendations": recommendations,
            "individual_risk_scores": risk_scores,
            "confidence_scores": confidence_scores,
            "deliberation_summary": self._summarize_deliberation(deliberation_transcript)
        }
    
    def _prepare_context(self, context: Dict) -> Dict:
        """Prepare context for sharing"""
        return {
            k: v.__dict__ if hasattr(v, '__dict__') else v
            for k, v in context.items()
        }
    
    def _check_early_consensus(self, messages: List[Dict]) -> bool:
        """Check if agents reached consensus early"""
        recommendations = [
            msg['message'].lower() 
            for msg in messages 
            if 'approve' in msg['message'].lower() or 'reject' in msg['message'].lower()
        ]
        
        # If all agents have same recommendation
        if len(set(recommendations)) == 1:
            return True
        
        return False
    
    def _summarize_deliberation(self, transcript: Dict) -> str:
        """Summarize the deliberation process"""
        summary_parts = []
        
        for round_data in transcript.get("rounds", []):
            round_num = round_data["round"]
            summary_parts.append(f"Round {round_num}:")
            
            for msg in round_data["messages"]:
                agent = msg["agent"]
                content = msg["message"][:200] + "..." if len(msg["message"]) > 200 else msg["message"]
                summary_parts.append(f"  - {agent}: {content}")
        
        return "\n".join(summary_parts)
```

---

## 5. MCP Integration

### 5.1 MCP Server Configuration (`mcp/mcp_config.json`)

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "google-maps": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-maps"],
      "env": {
        "GOOGLE_MAPS_API_KEY": "${GOOGLE_MAPS_API_KEY}"
      }
    },
    "clearbit": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-clearbit"],
      "env": {
        "CLEARBIT_API_KEY": "${CLEARBIT_API_KEY}"
      }
    }
  }
}
```

### 5.2 Verification Agent with MCP (`agents/verification_agent.py`)

```python
from google.adk import Agent, MCPClient
from typing import Dict, Any
import asyncio

class VerificationAgent:
    def __init__(self):
        # Initialize MCP clients
        self.mcp_search = MCPClient(
            server_name="brave-search",
            config_path="./mcp/mcp_config.json"
        )
        
        self.mcp_maps = MCPClient(
            server_name="google-maps",
            config_path="./mcp/mcp_config.json"
        )
        
        self.mcp_clearbit = MCPClient(
            server_name="clearbit",
            config_path="./mcp/mcp_config.json"
        )
        
        # Initialize agent
        self.agent = Agent(
            name="verification_agent",
            model="gemini-2.0-flash-exp",
            temperature=0.2,
            system_prompt=self._get_system_prompt(),
            mcp_clients=[self.mcp_search, self.mcp_maps, self.mcp_clearbit]
        )
    
    def _get_system_prompt(self) -> str:
        return """You are a verification specialist with access to web search and external APIs.
        
        Your responsibilities:
        1. Verify university reputation and accreditation
        2. Validate company legitimacy and financial health
        3. Check address authenticity
        4. Benchmark salary against market data
        5. Cross-reference all customer-provided information
        
        Use multiple sources and cite your references. Be thorough and objective."""
    
    async def verify_information(
        self,
        education: Dict,
        employment: Dict,
        personal_info: Dict
    ) -> Dict[str, Any]:
        """
        Main verification entry point
        """
        # Run verifications in parallel
        verification_tasks = [
            self.verify_university(education['university'], education['education_level']),
            self.verify_company(employment['company_name'], employment.get('monthly_salary')),
            self.verify_address(personal_info['address']),
            self.benchmark_salary(
                employment.get('monthly_salary'),
                employment['company_name'],
                personal_info['address']
            )
        ]
        
        results = await asyncio.gather(*verification_tasks, return_exceptions=True)
        
        university_result, company_result, address_result, salary_benchmark = results
        
        # Aggregate results
        verification_result = {
            "agent_name": "verification_agent",
            "confidence_score": self._calculate_confidence(results),
            "university_verification": university_result,
            "company_verification": company_result,
            "address_verification": address_result,
            "salary_benchmark": salary_benchmark,
            "overall_legitimacy": self._assess_legitimacy(results),
            "risk_score": self._calculate_risk_score(results),
            "recommendation": self._make_recommendation(results),
            "reasoning": self._generate_reasoning(results)
        }
        
        return verification_result
    
    async def verify_university(self, university_name: str, education_level: str) -> Dict:
        """Verify university using web search"""
        search_queries = [
            f"{university_name} accreditation status",
            f"{university_name} official website",
            f"{university_name} world university rankings",
            f"Is {university_name} legitimate university"
        ]
        
        search_results = []
        for query in search_queries:
            result = await self.mcp_search.call_tool(
                "brave_web_search",
                {"query": query, "count": 5}
            )
            search_results.append(result)
        
        # Analyze search results with Gemini
        analysis = await self.agent.run(
            prompt=f"""Analyze these search results about {university_name}:
            
            {search_results}
            
            Determine:
            1. Is this a legitimate, accredited university?
            2. What is its reputation and ranking?
            3. Is the education level ({education_level}) offered there?
            4. Any red flags or concerns?
            
            Return JSON with: legitimacy (verified/questionable/fake), reputation_score (0-100),
            accreditation_status, ranking_info, sources[]
            """
        )
        
        return analysis
    
    async def verify_company(self, company_name: str, salary: float) -> Dict:
        """Verify company legitimacy"""
        # Search for company information
        company_search = await self.mcp_search.call_tool(
            "brave_web_search",
            {"query": f"{company_name} company profile", "count": 5}
        )
        
        # Try Clearbit for company data
        try:
            clearbit_data = await self.mcp_clearbit.call_tool(
                "company_lookup",
                {"domain": f"{company_name.lower().replace(' ', '')}.com"}
            )
        except:
            clearbit_data = None
        
        # Search for reviews
        reviews_search = await self.mcp_search.call_tool(
            "brave_web_search",
            {"query": f"{company_name} glassdoor reviews employee", "count": 3}
        )
        
        analysis = await self.agent.run(
            prompt=f"""Analyze this company information:
            
            Company: {company_name}
            Search Results: {company_search}
            Clearbit Data: {clearbit_data}
            Reviews: {reviews_search}
            
            Determine:
            1. Is this a legitimate company?
            2. What industry and size?
            3. Financial health?
            4. Employee reviews/reputation?
            5. Does salary ${salary} seem reasonable for this company?
            
            Return JSON with verification details.
            """
        )
        
        return analysis
    
    async def verify_address(self, address: str) -> Dict:
        """Verify address using geocoding"""
        geocode_result = await self.mcp_maps.call_tool(
            "geocode_address",
            {"address": address}
        )
        
        if geocode_result.get("status") == "OK":
            location = geocode_result["results"][0]
            return {
                "valid": True,
                "geocoded": True,
                "latitude": location["geometry"]["location"]["lat"],
                "longitude": location["geometry"]["location"]["lng"],
                "formatted_address": location["formatted_address"],
                "type": location.get("types", []),
                "confidence": "high"
            }
        else:
            return {
                "valid": False,
                "geocoded": False,
                "confidence": "low",
                "error": geocode_result.get("error_message")
            }
    
    async def benchmark_salary(
        self,
        reported_salary: float,
        company_name: str,
        location: str
    ) -> Dict:
        """Benchmark salary against market data"""
        # Extract location info
        city = location.split(",")[0] if "," in location else location
        
        search_queries = [
            f"average salary {company_name} {city}",
            f"salary range {city} market data",
            f"{company_name} employee salary statistics"
        ]
        
        search_results = []
        for query in search_queries:
            result = await self.mcp_search.call_tool(
                "brave_web_search",
                {"query": query, "count": 3}
            )
            search_results.append(result)
        
        analysis = await self.agent.run(
            prompt=f"""Analyze salary data:
            
            Reported Salary: ${reported_salary}/month
            Company: {company_name}
            Location: {city}
            Search Results: {search_results}
            
            Determine:
            1. Market salary range for this company/location
            2. Is reported salary within reasonable range?
            3. Percentile of reported salary
            4. Any red flags?
            
            Return JSON with benchmark analysis.
            """
        )
        
        return analysis
    
    def _calculate_confidence(self, results: list) -> float:
        """Calculate overall confidence score"""
        # Implementation
        return 0.85
    
    def _assess_legitimacy(self, results: list) -> str:
        """Assess overall legitimacy"""
        # Implementation
        return "verified"
    
    def _calculate_risk_score(self, results: list) -> int:
        """Calculate risk score based on verification"""
        # Implementation
        return 10
    
    def _make_recommendation(self, results: list) -> str:
        """Make recommendation"""
        # Implementation
        return "approve"
    
    def _generate_reasoning(self, results: list) -> str:
        """Generate explanation"""
        # Implementation
        return "All verifications passed successfully"
```

---

## 6. Decision Framework

### 6.1 Risk Scoring Model

```python
class RiskScoringModel:
    """
    Comprehensive risk scoring system
    """
    
    @staticmethod
    def calculate_aggregate_risk(
        bank_risk: int,
        salary_risk: int,
        verification_risk: int,
        loan_details: Dict
    ) -> Dict[str, Any]:
        """
        Calculate aggregate risk score (0-100, lower is better)
        """
        
        # Weighted risk calculation
        weights = {
            'bank_statement': 0.35,
            'salary_verification': 0.30,
            'external_verification': 0.20,
            'loan_characteristics': 0.15
        }
        
        # Sub-agent risks
        base_risk = (
            bank_risk * weights['bank_statement'] +
            salary_risk * weights['salary_verification'] +
            verification_risk * weights['external_verification']
        )
        
        # Loan-specific risk
        loan_risk = RiskScoringModel._calculate_loan_risk(loan_details)
        total_risk = base_risk + (loan_risk * weights['loan_characteristics'])
        
        # Risk categories
        if total_risk < 20:
            category = "LOW_RISK"
            recommendation = "APPROVE"
        elif total_risk < 40:
            category = "MODERATE_LOW_RISK"
            recommendation = "APPROVE"
        elif total_risk < 60:
            category = "MODERATE_RISK"
            recommendation = "MANUAL_REVIEW"
        elif total_risk < 75:
            category = "MODERATE_HIGH_RISK"
            recommendation = "REJECT"
        else:
            category = "HIGH_RISK"
            recommendation = "REJECT"
        
        return {
            "total_risk_score": round(total_risk, 2),
            "risk_category": category,
            "recommendation": recommendation,
            "component_risks": {
                "bank_statement": bank_risk,
                "salary_verification": salary_risk,
                "external_verification": verification_risk,
                "loan_characteristics": loan_risk
            },
            "weights": weights
        }
    
    @staticmethod
    def _calculate_loan_risk(loan_details: Dict) -> float:
        """Calculate risk based on loan characteristics"""
        risk = 0
        
        # Loan amount risk
        amount = loan_details.get('loan_amount', 0)
        if amount > 100000:
            risk += 15
        elif amount > 50000:
            risk += 10
        elif amount > 25000:
            risk += 5
        
        # Duration risk
        duration = loan_details.get('loan_duration', 0)
        if duration > 60:  # > 5 years
            risk += 10
        elif duration > 36:
            risk += 5
        
        # Purpose risk
        purpose = loan_details.get('loan_purpose', '')
        high_risk_purposes = ['business', 'others']
        if purpose in high_risk_purposes:
            risk += 10
        
        return min(risk, 100)
```

### 6.2 Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DECISION MATRIX                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Risk Score Range    │  Category           │  Decision              │
│  ─────────────────────────────────────────────────────────────────  │
│  0-20               │  LOW                │  AUTO-APPROVE          │
│  21-40              │  MODERATE-LOW       │  AUTO-APPROVE          │
│  41-60              │  MODERATE           │  MANUAL REVIEW         │
│  61-75              │  MODERATE-HIGH      │  AUTO-REJECT           │
│  76-100             │  HIGH               │  AUTO-REJECT           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                   OVERRIDE CONDITIONS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Document Fraud Detected        →  IMMEDIATE REJECT             │
│  2. Income Verification Failed     →  MANUAL REVIEW                │
│  3. Multiple Red Flags (>3)        →  REJECT                       │
│  4. Consensus Strength < 0.6       →  MANUAL REVIEW                │
│  5. Agent Disagreement             →  MANUAL REVIEW                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.3 Loan Officer Decision Logic

```python
class LoanOfficerDecisionEngine:
    """
    Final decision making logic for Loan Officer Agent
    """
    
    async def make_decision(
        self,
        application: LoanApplication,
        sub_agent_results: Dict,
        consensus: Dict,
        deliberation: Dict
    ) -> DecisionResult:
        """
        Make final loan decision
        """
        
        # Calculate aggregate risk
        risk_analysis = RiskScoringModel.calculate_aggregate_risk(
            bank_risk=sub_agent_results['bank_analysis'].risk_score,
            salary_risk=sub_agent_results['salary_analysis'].risk_score,
            verification_risk=sub_agent_results['verification'].risk_score,
            loan_details=application.loan_request
        )
        
        # Check override conditions
        override_decision = self._check_override_conditions(
            sub_agent_results,
            consensus
        )
        
        if override_decision:
            return override_decision
        
        # Make decision based on risk score
        base_decision = risk_analysis['recommendation']
        
        # Consider consensus
        if consensus['consensus_strength'] < 0.6:
            base_decision = "MANUAL_REVIEW"
        
        # Calculate recommended loan terms
        loan_terms = self._calculate_loan_terms(
            application,
            risk_analysis['total_risk_score']
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            risk_analysis,
            sub_agent_results,
            consensus,
            base_decision
        )
        
        return DecisionResult(
            decision=base_decision,
            risk_score=risk_analysis['total_risk_score'],
            risk_category=risk_analysis['risk_category'],
            confidence_score=consensus.get('consensus_strength', 0),
            approved_amount=loan_terms['approved_amount'],
            interest_rate=loan_terms['interest_rate'],
            loan_duration=loan_terms['duration'],
            conditions=loan_terms.get('conditions', []),
            explanation=explanation,
            sub_agent_summaries={
                'bank_statement': sub_agent_results['bank_analysis'].reasoning,
                'salary_verification': sub_agent_results['salary_analysis'].reasoning,
                'external_verification': sub_agent_results['verification'].reasoning
            },
            deliberation_summary=consensus.get('deliberation_summary', ''),
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _check_override_conditions(self, results: Dict, consensus: Dict) -> Optional[DecisionResult]:
        """Check for conditions that override normal decision logic"""
        
        # Document fraud detected
        for agent_result in results.values():
            if hasattr(agent_result, 'red_flags'):
                fraud_flags = [f for f in agent_result.red_flags if f.get('type') == 'fraud']
                if fraud_flags:
                    return DecisionResult(
                        decision="REJECT",
                        risk_score=100,
                        explanation="Document fraud detected. Application rejected.",
                        conditions=["FRAUD_DETECTED"]
                    )
        
        # Multiple red flags
        total_red_flags = sum(
            len(getattr(result, 'red_flags', []))
            for result in results.values()
        )
        if total_red_flags >= 3:
            return DecisionResult(
                decision="REJECT",
                risk_score=85,
                explanation=f"Multiple red flags detected ({total_red_flags}). Application rejected."
            )
        
        return None
    
    def _calculate_loan_terms(self, application: LoanApplication, risk_score: float) -> Dict:
        """Calculate loan terms based on risk"""
        requested_amount = application.loan_request['loan_amount']
        requested_duration = application.loan_request['loan_duration']
        
        # Adjust amount based on risk
        if risk_score < 20:
            approved_amount = requested_amount
            interest_rate = 3.5  # Low risk rate
        elif risk_score < 40:
            approved_amount = requested_amount * 0.9
            interest_rate = 5.5
        elif risk_score < 60:
            approved_amount = requested_amount * 0.7
            interest_rate = 7.5
        else:
            approved_amount = 0
            interest_rate = 0
        
        conditions = []
        if risk_score > 30:
            conditions.append("Requires co-signer")
        if risk_score > 40:
            conditions.append("Additional collateral required")
        
        return {
            "approved_amount": round(approved_amount, 2),
            "interest_rate": interest_rate,
            "duration": requested_duration,
            "conditions": conditions
        }
    
    def _generate_explanation(
        self,
        risk_analysis: Dict,
        sub_agent_results: Dict,
        consensus: Dict,
        decision: str
    ) -> str:
        """Generate human-readable explanation"""
        
        explanation_parts = [
            f"Decision: {decision}",
            f"Overall Risk Score: {risk_analysis['total_risk_score']}/100 ({risk_analysis['risk_category']})",
            "",
            "Analysis Summary:",
        ]
        
        # Add sub-agent summaries
        for agent_name, result in sub_agent_results.items():
            explanation_parts.append(
                f"- {agent_name}: {result.recommendation} (risk: {result.risk_score}, confidence: {result.confidence_score})"
            )
        
        explanation_parts.extend([
            "",
            f"Agent Consensus: {consensus['consensus_recommendation']} (strength: {consensus['consensus_strength']:.2f})",
            "",
            "Key Factors:",
        ])
        
        # Add key factors based on risk components
        for component, score in risk_analysis['component_risks'].items():
            if score > 50:
                explanation_parts.append(f"- ⚠️ High Risk: {component} ({score}/100)")
            elif score > 30:
                explanation_parts.append(f"- ⚙️ Moderate Risk: {component} ({score}/100)")
            else:
                explanation_parts.append(f"- ✓ Low Risk: {component} ({score}/100)")
        
        return "\n".join(explanation_parts)
```

---